import hashlib
import json
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from opentruth import OpenTruth
from opentruth.backup import restore_backup
from opentruth.locking import WorkspaceBusy


@pytest.mark.parametrize("release", ["v0.1.0", "v0.1.1"])
def test_frozen_legacy_workspace_migration(tmp_path, release):
    original = Path(__file__).parent / "fixtures" / "legacy" / release
    checksums = json.loads((original / "checksums.json").read_text())
    for name, expected in checksums.items():
        assert hashlib.sha256((original / name).read_bytes()).hexdigest() == expected
    workspace = tmp_path / "legacy"
    shutil.copytree(original, workspace)
    expected = json.loads((workspace / "expected.json").read_text())
    app = OpenTruth(workspace)
    assert app.db.execute("PRAGMA user_version").fetchone()[0] == 2
    current = app.export_evidence()
    for table in ("claims", "sources", "evidence_links", "claim_revisions", "conflict_records"):
        assert current[table] == expected[table]
    assert current["review_events"][:-1] == expected["review_events"]
    assert app.verify_sources()["sources"][0]["integrity_status"] == "INTACT"
    claim_id = expected["claims"][0]["id"]
    app.revise_claim(claim_id, "new synthetic revision", value=2)
    assert app.search_claims("legacy")[0]["value"] == 2
    app.backup("upgraded.zip")
    app.close()
    restore_backup(workspace, "upgraded.zip", "restored")
    restored = OpenTruth(workspace, "restored")
    assert len(restored.inspect_claim(claim_id)["revisions"]) == 3
    restored.close()
    for name, digest in checksums.items():
        assert hashlib.sha256((original / name).read_bytes()).hexdigest() == digest


def test_indexed_pagination_and_lightweight_search(tmp_path, monkeypatch):
    app = OpenTruth(tmp_path)
    ids = [
        app.add_claim(f"SYNTHETIC beam {i}", subject="beam", predicate="length")["id"]
        for i in range(215)
    ]
    app.add_claim("SYNTHETIC unrelated", subject="other")
    monkeypatch.setattr(app, "get_claim_history", lambda *a, **k: pytest.fail("History was loaded"))
    pages = [app.search_claims(subject="beam", limit=80, offset=n) for n in (0, 80, 160)]
    assert [row["id"] for page in pages for row in page] == ids
    assert len(app.search_claims()) == 100
    assert all("history" not in row and "revisions" not in row for page in pages for row in page)
    plan = app.db.execute(
        "EXPLAIN QUERY PLAN SELECT id FROM claims WHERE "
        "json_extract(payload,'$.subject')=? AND "
        "json_extract(payload,'$.predicate')=?",
        ("beam", "length"),
    ).fetchall()
    assert "claims_subject_predicate" in str(plan)
    app.close()


@pytest.mark.parametrize("limit,offset", [(0, 0), (1001, 0), (True, 0), (1, -1)])
def test_invalid_pages(tmp_path, limit, offset):
    app = OpenTruth(tmp_path)
    with pytest.raises(ValueError):
        app.search_claims(limit=limit, offset=offset)
    app.close()


def test_fts_survives_reopen_without_rebuild(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim("SYNTHETIC original")
    app.close()
    app = OpenTruth(tmp_path)
    traced = []
    app.db.set_trace_callback(traced.append)
    app.revise_claim(a["id"], "synthetic correction", original_statement="SYNTHETIC revised")
    assert app.search_claims("revised")[0]["id"] == a["id"]
    assert app.search_claims("original") == []
    assert not any("DELETE FROM claim_search" in query for query in traced)
    app.close()


def test_conflict_batches_have_compact_audit_events(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim(
        "SYNTHETIC 1",
        subject="beam",
        predicate="length",
        value=1,
        unit="m",
        context={"method": "synthetic"},
    )
    for i in range(130):
        app.add_claim(
            f"SYNTHETIC {i}",
            subject="beam",
            predicate="length",
            value=i,
            unit="m",
            context=a["context"],
        )
    first = app.check_conflicts(a["id"])
    second = app.check_conflicts(a["id"], offset=100)
    assert len(first) == 100 and len(second) == 30
    assert {r["claim_ids"][1] for r in first}.isdisjoint(r["claim_ids"][1] for r in second)
    events = app.get_claim_history(a["id"])
    assert len(events[-1]["details"]["comparison_ids"]) == 30
    assert "comparisons" not in events[-1]["details"]
    assert app.get_claim_history(a["id"], limit=1, offset=1) == [events[1]]
    app.close()


def test_shared_instance_thread_serialization(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim("SYNTHETIC")
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(
            executor.map(
                lambda n: app.revise_claim(a["id"], "synthetic change", value=n), range(16)
            )
        )
    assert len(app.inspect_claim(a["id"])["revisions"]) == 17
    app.close()


def test_cross_process_busy_and_crash_recovery(tmp_path):
    app = OpenTruth(tmp_path, lock_timeout=0.05)
    script = """
import sys,time
from pathlib import Path
from opentruth import OpenTruth
app=OpenTruth(sys.argv[1])
with app._operation_lock:
 Path(sys.argv[1],"ready").touch()
 time.sleep(20)
"""
    child = subprocess.Popen([sys.executable, "-c", script, str(tmp_path)])
    try:
        deadline = time.monotonic() + 10
        while (
            not (tmp_path / "ready").exists()
            and child.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.01)
        assert (tmp_path / "ready").exists()
        with pytest.raises(WorkspaceBusy):
            app.add_claim("SYNTHETIC blocked")
        with pytest.raises(WorkspaceBusy):
            app.backup("blocked.zip")
        with pytest.raises(WorkspaceBusy):
            restore_backup(tmp_path, "unused.zip", lock_timeout=0.05)
        cli = subprocess.run(
            [
                sys.executable,
                "-m",
                "opentruth.cli",
                "--workspace",
                str(tmp_path),
                "--lock-timeout",
                "0.05",
                "init",
            ],
            capture_output=True,
            check=False,
            text=True,
            timeout=5,
        )
        assert cli.returncode == 1
        assert json.loads(cli.stderr)["error"] == "WORKSPACE_BUSY"
    finally:
        child.terminate()
        child.wait(timeout=5)
    assert not (tmp_path / "blocked.zip").exists()
    app.add_claim("SYNTHETIC after crash")
    assert len(app.search_claims()) == 1
    app.close()


def test_restore_frozen_schema_one_archive(tmp_path):
    archive = Path(__file__).parent / "fixtures/legacy/v0.1.1/snapshot.zip"
    shutil.copyfile(archive, tmp_path / "legacy.zip")
    restore_backup(tmp_path, "legacy.zip")
    app = OpenTruth(tmp_path)
    assert app.db.execute("PRAGMA user_version").fetchone()[0] == 2
    assert app.verify_sources()["sources"][0]["integrity_status"] == "INTACT"
    assert app.search_claims("legacy")[0]["provenance"]["release"] == "v0.1.1"
    app.close()


def test_failed_migration_keeps_original_schema_and_data(tmp_path):
    import sqlite3

    from opentruth.database import SCHEMA

    root = tmp_path / ".opentruth"
    root.mkdir()
    path = root / "evidence.sqlite3"
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    db.execute("PRAGMA user_version=1")
    db.execute("INSERT INTO claims VALUES ('synthetic-corrupt-record','invalid JSON')")
    db.commit()
    db.close()
    with pytest.raises(sqlite3.Error, match="malformed JSON"):
        OpenTruth(tmp_path)
    db = sqlite3.connect(path)
    assert db.execute("PRAGMA user_version").fetchone()[0] == 1
    assert db.execute("SELECT payload FROM claims").fetchone()[0] == "invalid JSON"
    assert not db.execute(
        "SELECT 1 FROM sqlite_master WHERE name='claims_subject_predicate'"
    ).fetchone()
    db.close()


def test_complete_executable_tutorial(tmp_path):
    from examples.tutorial import run

    assert run(tmp_path) == {
        "synthetic": True,
        "evidence_status": "CONTRADICTED_BY_REGISTERED_EVIDENCE",
        "history_events": 5,
        "backup_restored": True,
        "scientific_verification": "NOT_EVALUATED",
    }
