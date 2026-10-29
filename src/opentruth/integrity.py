"""Byte integrity checks, deliberately separate from scientific verification."""

import hashlib
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import UUID


def source_reference(source):
    reference = source.get("file_reference")
    if reference is None:
        return None
    identifier = str(UUID(source["id"]))
    if reference != f"files/{identifier}":
        raise ValueError("Unsafe stored source reference")
    return Path("files") / identifier


@contextmanager
def open_source(engine, source):
    reference = source_reference(source)
    if reference is None:
        raise ValueError("Source has no stored file")
    relative = engine.root.relative_to(engine.workspace) / reference
    if hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd:
        with engine._source_file(relative) as stream:
            yield stream
    else:
        # Windows: integrity reading in a trusted, non-concurrently-mutated workspace.
        path = engine.workspace
        for part in relative.parts:
            path /= part
            if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
                raise ValueError("Unsafe stored source path")
        if not path.resolve().is_relative_to(engine.workspace) or not path.is_file():
            raise ValueError("Unsafe stored source path")
        if path.stat().st_size > 20 * 1024 * 1024:
            raise ValueError("Stored file exceeds size limit")
        with path.open("rb") as stream:
            yield stream


def digest_stream(stream, limit=20 * 1024 * 1024):
    digest = hashlib.sha256()
    size = 0
    while block := stream.read(65536):
        size += len(block)
        if size > limit:
            raise ValueError("File exceeds size limit")
        digest.update(block)
    return digest.hexdigest(), size


def verify_sources(engine, source_id=None):
    import json

    sources = (
        [engine._get("sources", source_id)]
        if source_id
        else [
            json.loads(row[0])
            for row in engine.db.execute("SELECT payload FROM sources ORDER BY rowid")
        ]
    )
    results = []
    for source in sources:
        record = {
            "source_id": source["id"],
            "expected_sha256": source.get("sha256"),
            "actual_sha256": None,
            "integrity_status": "NO_LOCAL_FILE",
        }
        if source.get("file_reference") is not None:
            try:
                with open_source(engine, source) as stream:
                    digest, size = digest_stream(stream)
                record.update(
                    actual_sha256=digest,
                    size_bytes=size,
                    integrity_status="INTACT" if digest == source["sha256"] else "ALTERED",
                )
            except FileNotFoundError:
                record["integrity_status"] = "MISSING"
            except (OSError, ValueError):
                record["integrity_status"] = "UNREADABLE_OR_UNSAFE"
        results.append(record)
    return {
        "scientific_verification": "NOT_EVALUATED",
        "sources": results,
        "ok": all(r["integrity_status"] in {"INTACT", "NO_LOCAL_FILE"} for r in results),
    }
