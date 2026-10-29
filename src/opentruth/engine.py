"""Shared transactional evidence engine, independent of CLI and MCP."""

import hashlib
import json
import os
import sqlite3
import stat
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID, uuid4

from pydantic import TypeAdapter

from .conflicts import compare, validate_tolerances
from .contexts import context_warnings
from .database import connect
from .models import Claim, Link, Review, Source


def now():
    return datetime.now(UTC).isoformat()


def encoded(value):
    text = json.dumps(value, ensure_ascii=False, allow_nan=False)
    if len(text.encode()) > 100000:
        raise ValueError("Record exceeds 100 KB limit")
    return text


class OpenTruth:
    def __init__(self, workspace=".", data_dir=".opentruth"):
        self.workspace = Path(workspace).resolve(strict=True)
        relative = Path(data_dir)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Data directory must be workspace-relative without traversal")
        current = self.workspace
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                raise ValueError("Unsafe data directory")
        self.root = self.workspace / relative
        # Data and source paths must remain in the configured workspace.
        if not self.root.resolve().is_relative_to(self.workspace):
            raise ValueError("Data directory escapes workspace")
        self.root.mkdir(parents=True, exist_ok=True)
        self.files = self.root / "files"
        self.files.mkdir(exist_ok=True)
        if self.files.is_symlink() or not self.files.resolve().is_relative_to(self.workspace):
            raise ValueError("Unsafe storage directory")
        dbpath = self.root / "evidence.sqlite3"
        if dbpath.is_symlink():
            raise ValueError("Unsafe database path")
        self.db = connect(dbpath)
        self.fts = True
        try:
            self.db.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS claim_search USING fts5(id UNINDEXED, statement)"
            )
            # Rebuild from authoritative records, including DBs created without FTS5.
            with self.db:
                self.db.execute("DELETE FROM claim_search")
                for record in self.db.execute("SELECT id,payload FROM claims").fetchall():
                    self.db.execute(
                        "INSERT INTO claim_search VALUES (?,?)",
                        (record[0], json.loads(record[1])["original_statement"]),
                    )
        except sqlite3.OperationalError as error:
            if "no such module" not in str(error):
                raise
            self.fts = False

    def close(self):
        self.db.close()

    def _get(self, table, identifier):
        UUID(identifier)
        # table is an internal constant, never supplied through public interfaces.
        row = self.db.execute(f"SELECT payload FROM {table} WHERE id=?", (identifier,)).fetchone()
        if row is None:
            raise ValueError("Unknown record identifier")
        return json.loads(row[0])

    def _event(self, action, entity, actor, details):
        event = {
            "timestamp": now(),
            "action": action,
            "entity_id": entity,
            "actor": actor,
            "details": details,
        }
        self.db.execute(
            "INSERT INTO review_events(entity_id,payload) VALUES (?,?)", (entity, encoded(event))
        )

    def add_claim(self, original_statement, actor=None, **attributes):
        data = Claim(original_statement=original_statement, **attributes).model_dump()
        data.update(
            id=str(uuid4()),
            normalized_statement=" ".join(original_statement.split()),
            created_at=now(),
            review_status="NEEDS_REVIEW",
        )
        with self.db:
            self.db.execute("INSERT INTO claims VALUES (?,?)", (data["id"], encoded(data)))
            self.db.execute(
                "INSERT INTO claim_revisions(claim_id,payload) VALUES (?,?)",
                (data["id"], encoded(data)),
            )
            if self.fts:
                self.db.execute(
                    "INSERT INTO claim_search VALUES (?,?)", (data["id"], original_statement)
                )
            self._event("CLAIM_CREATED", data["id"], actor, data)
        return dict(
            data, context_warnings=context_warnings(data["context"], data["context_template"])
        )

    def revise_claim(self, claim_id, reason, actor=None, **changes):
        if not reason.strip():
            raise ValueError("Revision reason required")
        old = self._get("claims", claim_id)
        candidate = {k: old[k] for k in Claim.model_fields if k in old}
        candidate.update(changes)
        data = Claim(**candidate).model_dump()
        data.update(
            id=claim_id,
            created_at=old["created_at"],
            review_status="NEEDS_REVIEW",
            normalized_statement=" ".join(data["original_statement"].split()),
        )
        with self.db:
            self.db.execute("UPDATE claims SET payload=? WHERE id=?", (encoded(data), claim_id))
            self.db.execute(
                "INSERT INTO claim_revisions(claim_id,payload) VALUES (?,?)",
                (claim_id, encoded(data)),
            )
            if self.fts:
                self.db.execute(
                    "UPDATE claim_search SET statement=? WHERE id=?",
                    (data["original_statement"], claim_id),
                )
            self._event("CLAIM_REVISED", claim_id, actor, {"reason": reason, "revision": data})
        return dict(
            data, context_warnings=context_warnings(data["context"], data["context_template"])
        )

    @contextmanager
    def _source_file(self, relative):
        directory = os.open(self.workspace, os.O_RDONLY | os.O_DIRECTORY)
        try:
            parts = relative.parts
            if not parts:
                raise ValueError("Source must be a regular file")
            for part in parts[:-1]:
                child = os.open(
                    part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory
                )
                os.close(directory)
                directory = child
            descriptor = os.open(
                parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory
            )
            with os.fdopen(descriptor, "rb") as source:
                info = os.fstat(source.fileno())
                if not stat.S_ISREG(info.st_mode) or info.st_size > 20 * 1024 * 1024:
                    raise ValueError("Source must be a regular file at most 20 MiB")
                yield source
        finally:
            os.close(directory)

    def register_source(self, title, actor=None, **attributes):
        model = Source(title=title, **attributes)
        data = model.model_dump(exclude={"file_path"})
        data.update(
            id=str(uuid4()),
            registered_at=now(),
            verification_status="NOT_EVALUATED",
            file_reference=None,
            sha256=None,
            original_filename=None,
        )
        target = None
        copied = False
        if model.file_path:
            path = Path(model.file_path)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("Source must use a workspace-relative path without traversal")
            # Open every component relative to a held directory descriptor. O_NOFOLLOW
            # prevents symlink replacement races between validation and opening.
            if not hasattr(os, "O_NOFOLLOW"):
                raise ValueError("Secure file copying is not supported on this platform")
            target = self.files / data["id"]
            digest = hashlib.sha256()
            try:
                with self._source_file(path) as source, target.open("xb") as dest:
                    copied = True
                    total = 0
                    while block := source.read(65536):
                        total += len(block)
                        if total > 20 * 1024 * 1024:
                            raise ValueError("Source exceeds 20 MiB limit")
                        digest.update(block)
                        dest.write(block)
            except BaseException:
                if copied:
                    target.unlink(missing_ok=True)
                raise
            data.update(
                file_reference="files/" + data["id"],
                sha256=digest.hexdigest(),
                original_filename=path.name,
            )
        try:
            with self.db:
                self.db.execute("INSERT INTO sources VALUES (?,?)", (data["id"], encoded(data)))
                self._event("SOURCE_REGISTERED", data["id"], actor, data)
        except BaseException:
            if target:
                target.unlink(missing_ok=True)
            raise
        return data

    def link_evidence(self, claim_id, source_id, relationship, source_location, excerpt, actor):
        data = Link(
            claim_id=claim_id,
            source_id=source_id,
            relationship=relationship,
            source_location=source_location,
            excerpt=excerpt,
            actor=actor,
        ).model_dump()
        self._get("claims", claim_id)
        self._get("sources", source_id)
        data.update(
            id=str(uuid4()),
            created_at=now(),
            review_status="NEEDS_REVIEW",
            claim_revision=self._revision_number(claim_id),
        )
        with self.db:
            self.db.execute(
                "INSERT INTO evidence_links VALUES (?,?,?,?)",
                (data["id"], claim_id, source_id, encoded(data)),
            )
            self._event("EVIDENCE_LINKED", claim_id, actor, data)
        return data

    def revise_evidence(self, link_id, reason, **changes):
        if not reason.strip():
            raise ValueError("Revision reason required")
        old = self._get("evidence_links", link_id)
        data = {k: old[k] for k in Link.model_fields}
        if set(changes) - {"relationship", "source_location", "excerpt", "actor"}:
            raise ValueError("Evidence endpoints cannot be changed")
        data.update(changes)
        data = Link(**data).model_dump()
        data.update(
            id=link_id,
            created_at=old["created_at"],
            review_status="NEEDS_REVIEW",
            claim_revision=self._revision_number(data["claim_id"]),
        )
        with self.db:
            self.db.execute(
                "UPDATE evidence_links SET payload=? WHERE id=?", (encoded(data), link_id)
            )
            self._event(
                "EVIDENCE_REVISED",
                data["claim_id"],
                data["actor"],
                {"reason": reason, "previous": old, "revision": data},
            )
        return data

    def review_claim(self, claim_id, decision, reason="", actor=None):
        decision = TypeAdapter(Review).validate_python(decision)
        if not isinstance(reason, str) or (
            decision in {"ACCEPTED_FOR_USE", "REJECTED"} and not reason.strip()
        ):
            raise ValueError("Acceptance and rejection require a reason")
        if actor is not None and (not isinstance(actor, str) or not actor.strip()):
            raise ValueError("Provided actor must not be blank")
        data = self._get("claims", claim_id)
        data["review_status"] = decision
        with self.db:
            self.db.execute("UPDATE claims SET payload=? WHERE id=?", (encoded(data), claim_id))
            self._event("HUMAN_REVIEW", claim_id, actor, {"decision": decision, "reason": reason})
        return data

    def get_claim_history(self, claim_id):
        self._get("claims", claim_id)
        return [
            json.loads(r[0])
            for r in self.db.execute(
                "SELECT payload FROM review_events WHERE entity_id=? ORDER BY sequence", (claim_id,)
            )
        ]

    def _revision_number(self, claim_id):
        return self.db.execute(
            "SELECT COUNT(*) FROM claim_revisions WHERE claim_id=?", (claim_id,)
        ).fetchone()[0]

    def inspect_claim(self, claim_id):
        data = self._get("claims", claim_id)
        data["context_warnings"] = context_warnings(data["context"], data.get("context_template"))
        links = [
            json.loads(r[0])
            for r in self.db.execute(
                "SELECT payload FROM evidence_links WHERE claim_id=? ORDER BY rowid", (claim_id,)
            )
        ]
        data["revision_number"] = self._revision_number(claim_id)
        data["evidence"] = [
            dict(
                link,
                source=self._get("sources", link["source_id"]),
                applies_to_current_revision=(
                    link.get("claim_revision", 1) == data["revision_number"]
                ),
            )
            for link in links
        ]
        types = {
            link["relationship"] for link in data["evidence"] if link["applies_to_current_revision"]
        }
        data["evidence_status"] = (
            "CONFLICTING_REGISTERED_EVIDENCE"
            if {"SUPPORTS", "CONTRADICTS"} <= types
            else "SUPPORTED_BY_REGISTERED_EVIDENCE"
            if "SUPPORTS" in types
            else "CONTRADICTED_BY_REGISTERED_EVIDENCE"
            if "CONTRADICTS" in types
            else "INSUFFICIENT_EVIDENCE"
        )
        data["revisions"] = [
            json.loads(r[0])
            for r in self.db.execute(
                "SELECT payload FROM claim_revisions WHERE claim_id=? ORDER BY sequence",
                (claim_id,),
            )
        ]
        data["history"] = self.get_claim_history(claim_id)
        data["potential_conflicts"] = [
            json.loads(r[0])
            for r in self.db.execute(
                "SELECT payload FROM conflict_records WHERE claim_id=? ORDER BY rowid", (claim_id,)
            )
        ]
        return data

    def search_claims(
        self, query="", exact_phrase=False, subject=None, predicate=None, review_status=None
    ):
        if len(query) > 20000:
            raise ValueError("Query too long")
        candidates = None
        if query and self.fts:
            tokens = [query] if exact_phrase else query.split()
            expression = " AND ".join('"' + token.replace('"', '""') + '"' for token in tokens)
            if expression:
                candidates = {
                    r[0]
                    for r in self.db.execute(
                        "SELECT id FROM claim_search WHERE statement MATCH ?", (expression,)
                    )
                }
        result = []
        for row in self.db.execute("SELECT payload FROM claims ORDER BY rowid"):
            data = json.loads(row[0])
            text = data["original_statement"].casefold()
            matches = (
                query.casefold() in text
                if exact_phrase
                else all(token.casefold() in text for token in query.split())
            )
            if candidates is not None:
                matches = data["id"] in candidates
            if not matches or any(
                value is not None and data[key] != value
                for key, value in (
                    ("subject", subject),
                    ("predicate", predicate),
                    ("review_status", review_status),
                )
            ):
                continue
            result.append(self.inspect_claim(data["id"]))
        return result

    def check_conflicts(self, claim_id, abs_tol=0.0, rel_tol=1e-9, actor=None):
        validate_tolerances(abs_tol, rel_tol)
        claim = self._get("claims", claim_id)
        records = []
        with self.db:
            for row in self.db.execute(
                "SELECT payload FROM claims WHERE id != ?", (claim_id,)
            ).fetchall():
                other = json.loads(row[0])
                if (claim["subject"], claim["predicate"]) != (other["subject"], other["predicate"]):
                    continue
                record = compare(claim, other, abs_tol, rel_tol)
                record.update(id=str(uuid4()), detected_at=now())
                records.append(record)
                self.db.execute(
                    "INSERT INTO conflict_records VALUES (?,?,?)",
                    (record["id"], claim_id, encoded(record)),
                )
            self._event("CONFLICT_CHECK", claim_id, actor, {"comparisons": records})
        return records

    def export_evidence(self, actor=None):
        with self.db:
            self._event("EXPORT", "collection", actor, {"schema_version": 1})
            result = {"schema_version": 1, "exported_at": now(), "files_included": False}
            for table in (
                "claims",
                "sources",
                "evidence_links",
                "claim_revisions",
                "review_events",
                "conflict_records",
            ):
                result[table] = [
                    json.loads(r[0])
                    for r in self.db.execute(f"SELECT payload FROM {table} ORDER BY rowid")
                ]
        return result

    def verify_sources(self, source_id=None):
        """Compare stored bytes with recorded hashes; never verify scientific content."""
        from .integrity import verify_sources

        return verify_sources(self, source_id)

    def backup(self, archive_path):
        """Create a complete, consistent backup without overwriting an existing archive."""
        from .backup import create_backup

        return create_backup(self, archive_path)
