import hashlib
import json
import sqlite3
import zipfile

import pytest

from opentruth import OpenTruth
from opentruth.backup import restore_backup


@pytest.fixture
def evidence(tmp_path):
    app = OpenTruth(tmp_path)
    (tmp_path / "synthetic.txt").write_bytes(b"SYNTHETIC source bytes")
    source = app.register_source("SYNTHETIC source", file_path="synthetic.txt")
    claim = app.add_claim("SYNTHETIC original", provenance={"synthetic": True})
    app.link_evidence(claim["id"], source["id"], "SUPPORTS", "table 1", "synthetic", "tester")
    app.revise_claim(claim["id"], "synthetic revision", original_statement="SYNTHETIC revised")
    app.review_claim(claim["id"], "ACCEPTED_FOR_USE", "synthetic decision", "tester")
    yield app, claim, source
    app.close()


def test_complete_backup_round_trip(evidence, tmp_path):
    app, claim, source = evidence
    before = app.inspect_claim(claim["id"])
    result = app.backup("evidence.zip")
    assert result["members"] == 2
    restore_backup(tmp_path, "evidence.zip", "restored")
    restored = OpenTruth(tmp_path, data_dir="restored")
    try:
        assert restored.inspect_claim(claim["id"]) == before
        assert restored.verify_sources()["sources"][0]["integrity_status"] == "INTACT"
        assert (restored.root / source["file_reference"]).read_bytes() == b"SYNTHETIC source bytes"
        assert restored.export_evidence()["sources"][0]["sha256"] == source["sha256"]
    finally:
        restored.close()
    assert app.inspect_claim(claim["id"]) == before


@pytest.mark.parametrize(
    "mode,status",
    [("modify", "ALTERED"), ("delete", "MISSING"), ("symlink", "UNREADABLE_OR_UNSAFE")],
)
def test_integrity_does_not_promote_source_verification(evidence, tmp_path, mode, status):
    app, _, source = evidence
    path = app.root / source["file_reference"]
    if mode == "modify":
        path.write_bytes(b"SYNTHETIC altered")
    else:
        path.unlink()
        if mode == "symlink":
            path.symlink_to(tmp_path / "synthetic.txt")
    report = app.verify_sources(source["id"])
    assert report["ok"] is False
    assert report["sources"][0]["integrity_status"] == status
    assert app._get("sources", source["id"])["verification_status"] == "NOT_EVALUATED"
    with pytest.raises((ValueError, OSError)):
        app.backup("invalid.zip")
    assert not (tmp_path / "invalid.zip").exists()


def test_metadata_only_integrity_and_backup(tmp_path):
    app = OpenTruth(tmp_path)
    source = app.register_source("SYNTHETIC metadata", url="https://example.invalid/paper")
    assert app.verify_sources(source["id"])["sources"][0]["integrity_status"] == "NO_LOCAL_FILE"
    app.backup("metadata.zip")
    app.close()
    restore_backup(tmp_path, "metadata.zip", "copy")
    restored = OpenTruth(tmp_path, "copy")
    assert restored.export_evidence()["sources"] == [source]
    restored.close()


def test_never_overwrite_archive_or_data(evidence, tmp_path):
    app, claim, _ = evidence
    app.backup("evidence.zip")
    checksum = hashlib.sha256((tmp_path / "evidence.zip").read_bytes()).hexdigest()
    with pytest.raises(FileExistsError):
        app.backup("evidence.zip")
    assert hashlib.sha256((tmp_path / "evidence.zip").read_bytes()).hexdigest() == checksum
    with pytest.raises(ValueError, match="absent"):
        restore_backup(tmp_path, "evidence.zip")
    assert app.inspect_claim(claim["id"])["review_status"] == "ACCEPTED_FOR_USE"


@pytest.mark.parametrize("path", ["../escape.zip", "/tmp/escape.zip", ".opentruth/backup.zip"])
def test_backup_paths_are_workspace_bounded(evidence, path):
    with pytest.raises(ValueError):
        evidence[0].backup(path)


def rewrite_archive(path, mutate):
    with zipfile.ZipFile(path) as archive:
        entries = {name: archive.read(name) for name in archive.namelist()}
    mutate(entries)
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in entries.items():
            archive.writestr(name, data)


@pytest.mark.parametrize(
    "mode",
    [
        "tamper",
        "traversal",
        "manifest",
        "version",
        "missing",
        "corrupt_database",
        "wrong_source_hash",
    ],
)
def test_invalid_archives_leave_no_destination(evidence, tmp_path, mode):
    app, _, source = evidence
    app.backup("evidence.zip")

    def mutate(entries):
        if mode == "tamper":
            entries[source["file_reference"]] = b"SYNTHETIC tampered"
        elif mode == "traversal":
            entries["../escape"] = b"escape"
        elif mode == "manifest":
            entries["manifest.json"] = b"[]"
        elif mode == "version":
            manifest = json.loads(entries["manifest.json"])
            manifest["backup_version"] = 99
            entries["manifest.json"] = json.dumps(manifest).encode()
        elif mode == "missing":
            del entries[source["file_reference"]]
        else:
            name = "evidence.sqlite3" if mode == "corrupt_database" else source["file_reference"]
            entries[name] = b"SYNTHETIC invalid"
            manifest = json.loads(entries["manifest.json"])
            manifest["members"][name] = {
                "sha256": hashlib.sha256(entries[name]).hexdigest(),
                "size": len(entries[name]),
            }
            entries["manifest.json"] = json.dumps(manifest).encode()

    rewrite_archive(tmp_path / "evidence.zip", mutate)
    with pytest.raises((ValueError, TypeError, sqlite3.Error)):
        restore_backup(tmp_path, "evidence.zip", "copy")
    assert not (tmp_path / "copy").exists()
    assert not (tmp_path / "escape").exists()
    assert list(tmp_path.glob(".opentruth-restore-*")) == []


def test_restore_limits_and_symlink_destination(evidence, tmp_path, monkeypatch):
    from opentruth import backup

    app = evidence[0]
    app.backup("evidence.zip")
    monkeypatch.setattr(backup, "MAX_TOTAL", 8)
    with pytest.raises(ValueError, match="limits"):
        restore_backup(tmp_path, "evidence.zip", "copy")
    (tmp_path / "link").symlink_to(tmp_path / "missing", target_is_directory=True)
    with pytest.raises(ValueError, match="Symlinks"):
        restore_backup(tmp_path, "evidence.zip", "link")
    assert not (tmp_path / "missing").exists()


def test_manifest_cannot_authorize_traversal(evidence, tmp_path):
    app = evidence[0]
    app.backup("evidence.zip")

    def mutate(entries):
        name = "files/../../escaped"
        entries[name] = b"SYNTHETIC"
        manifest = json.loads(entries["manifest.json"])
        manifest["members"][name] = {"size": 9, "sha256": hashlib.sha256(entries[name]).hexdigest()}
        entries["manifest.json"] = json.dumps(manifest).encode()

    rewrite_archive(tmp_path / "evidence.zip", mutate)
    with pytest.raises(ValueError):
        restore_backup(tmp_path, "evidence.zip", "copy")
    assert not (tmp_path / "escaped").exists()
    assert not (tmp_path / "copy").exists()


def test_duplicate_members_rejected(evidence, tmp_path):
    evidence[0].backup("evidence.zip")
    with (
        zipfile.ZipFile(tmp_path / "evidence.zip", "a") as archive,
        pytest.warns(UserWarning, match="Duplicate name"),
    ):
        archive.writestr("manifest.json", b"{}")
    with pytest.raises(ValueError, match="Duplicate"):
        restore_backup(tmp_path, "evidence.zip", "copy")
    assert not (tmp_path / "copy").exists()
