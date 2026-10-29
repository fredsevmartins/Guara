"""Versioned, bounded ZIP backups. Never extract archive-supplied paths."""

import hashlib
import json
import os
import shutil
import sqlite3
import tempfile
import zipfile
from pathlib import Path
from uuid import UUID

from .database import SCHEMA_VERSION
from .integrity import digest_stream, open_source, source_reference
from .locking import WorkspaceLock

MAX_DATABASE = 256 * 1024 * 1024
MAX_TOTAL = 1024 * 1024 * 1024
MAX_FILE = 20 * 1024 * 1024
MAX_MANIFEST = 8 * 1024 * 1024


def workspace_path(workspace, relative):
    workspace = Path(workspace).resolve(strict=True)
    relative = Path(relative)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("Path must be workspace-relative without traversal")
    current = workspace
    for part in relative.parts:
        current /= part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("Symlinks and junctions are not allowed")
    if not current.resolve().is_relative_to(workspace):
        raise ValueError("Path escapes workspace")
    return current


def create_backup(engine, archive_path):
    """Snapshot SQLite and copy registered source bytes; fail on missing/altered files."""
    destination = workspace_path(engine.workspace, archive_path)
    if destination.is_relative_to(engine.root):
        raise ValueError("Backup must be outside the live data directory")
    manifest = {"backup_version": 1, "schema_version": SCHEMA_VERSION, "members": {}}
    with tempfile.TemporaryDirectory(dir=engine.workspace, prefix=".opentruth-backup-") as staging:
        snapshot = Path(staging) / "evidence.sqlite3"
        db = sqlite3.connect(snapshot)
        try:
            engine.db.backup(db)
            sources = [json.loads(row[0]) for row in db.execute("SELECT payload FROM sources")]
            if sum(s.get("file_reference") is not None for s in sources) > 10000:
                raise ValueError("Too many stored files for backup format")
        finally:
            db.close()
        archive = Path(staging) / "backup.zip"
        total = 0
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_STORED) as output:

            def add(name, stream, limit):
                nonlocal total
                digest = hashlib.sha256()
                size = 0
                with output.open(name, "w", force_zip64=True) as target:
                    while block := stream.read(65536):
                        size += len(block)
                        total += len(block)
                        if size > limit or total > MAX_TOTAL:
                            raise ValueError("Backup exceeds supported size limits")
                        digest.update(block)
                        target.write(block)
                manifest["members"][name] = {"sha256": digest.hexdigest(), "size": size}
                return digest.hexdigest()

            with snapshot.open("rb") as stream:
                add("evidence.sqlite3", stream, MAX_DATABASE)
            for source in sources:
                reference = source_reference(source)
                if reference is not None:
                    with open_source(engine, source) as stream:
                        digest = add(reference.as_posix(), stream, MAX_FILE)
                    if digest != source["sha256"]:
                        raise ValueError("Source integrity mismatch; backup aborted")
            payload = json.dumps(manifest, allow_nan=False).encode()
            if len(payload) > MAX_MANIFEST:
                raise ValueError("Manifest exceeds size limit")
            output.writestr("manifest.json", payload)
        # Exclusive creation preserves any existing destination, even on failures.
        created = False
        try:
            flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
            descriptor = os.open(destination, flags, 0o600)
            with os.fdopen(descriptor, "wb") as target:
                created = True
                with archive.open("rb") as stream:
                    shutil.copyfileobj(stream, target)
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
    return {
        "status": "BACKUP_CREATED",
        "archive": str(Path(archive_path)),
        "members": len(manifest["members"]),
        "scientific_verification": "NOT_EVALUATED",
    }


def restore_backup(workspace, archive_path, data_dir=".opentruth", lock_timeout=5):
    workspace = Path(workspace).resolve(strict=True)
    workspace_path(workspace, data_dir)
    with WorkspaceLock(workspace, data_dir, lock_timeout):
        return _restore_backup(workspace, archive_path, data_dir)


def _restore_backup(workspace, archive_path, data_dir):
    """Verify all bytes and SQLite before restoring into a new data directory."""
    workspace = Path(workspace).resolve(strict=True)
    archive_path = workspace_path(workspace, archive_path)
    destination = workspace_path(workspace, data_dir)
    if destination.exists():
        raise ValueError("Restore requires an absent data directory; never overwrite live data")
    with tempfile.TemporaryDirectory(dir=workspace, prefix=".opentruth-restore-") as staging:
        root = Path(staging) / "data"
        root.mkdir(mode=0o700)
        (root / "files").mkdir(mode=0o700)
        with zipfile.ZipFile(archive_path) as archive:
            entries = archive.infolist()
            names = [entry.filename for entry in entries]
            if len(names) != len(set(names)) or len(names) > 10002:
                raise ValueError("Duplicate members or too many backup members")
            info = archive.getinfo("manifest.json")
            if info.file_size > MAX_MANIFEST:
                raise ValueError("Manifest exceeds size limit")
            manifest = json.loads(archive.read(info))
            if not isinstance(manifest, dict):
                raise TypeError("Backup manifest must be an object")
            if (
                manifest.get("backup_version") != 1
                or manifest.get("schema_version") not in range(1, SCHEMA_VERSION + 1)
            ):
                raise ValueError("Unsupported backup or database version")
            members = manifest["members"]
            if not isinstance(members, dict) or set(names) != {"manifest.json", *members}:
                raise ValueError("Backup membership differs from manifest")
            if "evidence.sqlite3" not in members:
                raise ValueError("Missing database")
            total = 0
            for name, expected in members.items():
                if name != "evidence.sqlite3" and (
                    not name.startswith("files/") or name != f"files/{UUID(name[6:])}"
                ):
                    raise ValueError("Unsafe archive member")
                entry = archive.getinfo(name)
                limit = MAX_DATABASE if name == "evidence.sqlite3" else MAX_FILE
                total += entry.file_size
                if entry.file_size > limit or total > MAX_TOTAL or entry.flag_bits & 1:
                    raise ValueError("Backup exceeds limits or is encrypted")
                if entry.file_size != expected["size"]:
                    raise ValueError("Backup size mismatch")
                # Member paths are an exact allowlist, not passed to extract/extractall.
                target = root / name
                with archive.open(entry) as source, target.open("xb") as output:
                    size = 0
                    while block := source.read(65536):
                        size += len(block)
                        if size > limit:
                            raise ValueError("Archive member exceeds size limit")
                        output.write(block)
                with target.open("rb") as source:
                    digest, _ = digest_stream(source, limit)
                if digest != expected["sha256"]:
                    raise ValueError("Backup checksum mismatch")
        db = sqlite3.connect(root / "evidence.sqlite3")
        try:
            if db.execute("PRAGMA user_version").fetchone()[0] != manifest["schema_version"]:
                raise ValueError("Database version differs from manifest")
            if db.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
                raise ValueError("Database integrity check failed")
            if db.execute("PRAGMA foreign_key_check").fetchall():
                raise ValueError("Database foreign key check failed")
            for table in (
                "claims",
                "sources",
                "evidence_links",
                "claim_revisions",
                "review_events",
                "conflict_records",
            ):
                for (payload,) in db.execute(f"SELECT payload FROM {table}"):
                    if not isinstance(json.loads(payload), dict):
                        raise TypeError("Invalid database record")
            referenced = {"evidence.sqlite3"}
            for (payload,) in db.execute("SELECT payload FROM sources"):
                source = json.loads(payload)
                reference = source_reference(source)
                if reference is not None:
                    name = reference.as_posix()
                    if name not in members or members[name]["sha256"] != source["sha256"]:
                        raise ValueError("Source bytes do not match database")
                    referenced.add(name)
            if referenced != set(members):
                raise ValueError("Unreferenced backup files")
        finally:
            db.close()
        # Offline operation: no concurrent writers/restores may mutate these trusted paths.
        if destination.exists():
            raise ValueError("Destination appeared during restore")
        os.rename(root, destination)
    return {
        "status": "RESTORED",
        "data_dir": str(Path(data_dir)),
        "scientific_verification": "NOT_EVALUATED",
    }
