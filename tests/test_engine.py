import hashlib
import json
import sqlite3
from uuid import uuid4

import pytest

from opentruth import OpenTruth
from opentruth.conflicts import compare


@pytest.fixture
def engine(tmp_path):
    app = OpenTruth(tmp_path)
    yield app
    app.close()


def test_workflow_revision_review_export_persistence(engine, tmp_path):
    original = "  Exact  original wording.\n"
    claim = engine.add_claim(original, provenance={"origin": "AI"})
    assert claim["original_statement"] == original
    assert engine.inspect_claim(claim["id"])["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    file = tmp_path / "source.txt"
    file.write_bytes(b"synthetic")
    source = engine.register_source("Synthetic source", file_path="source.txt")
    assert source["sha256"] == hashlib.sha256(b"synthetic").hexdigest()
    assert source["verification_status"] == "NOT_EVALUATED"
    link = engine.link_evidence(claim["id"], source["id"], "SUPPORTS", "p1", "excerpt", "tester")
    engine.revise_evidence(link["id"], "new interpretation", relationship="CONTRADICTS")
    engine.revise_claim(claim["id"], "clarification", original_statement="Updated wording")
    engine.review_claim(claim["id"], "ACCEPTED_FOR_USE", "Reviewed for synthetic use", "tester")
    record = engine.inspect_claim(claim["id"])
    assert record["revisions"][0]["original_statement"] == original
    assert record["review_status"] == "ACCEPTED_FOR_USE"
    assert len(record["history"]) == 5
    export = engine.export_evidence("tester")
    assert json.loads(json.dumps(export))["evidence_links"][0]["actor"] == "tester"
    reopened = OpenTruth(tmp_path)
    assert reopened.inspect_claim(claim["id"])["history"] == record["history"]
    assert reopened.export_evidence()["sources"][0]["sha256"] == source["sha256"]
    reopened.close()


@pytest.mark.parametrize(
    "kwargs",
    [
        {"original_statement": ""},
        {"original_statement": " "},
        {"original_statement": "x" * 20001},
        {"original_statement": "x", "value": float("nan")},
        {"original_statement": "x", "unexpected": True},
        {"original_statement": "x", "context": {"huge": "x" * 100001}},
    ],
)
def test_invalid_claim(engine, kwargs):
    with pytest.raises(ValueError):
        engine.add_claim(**kwargs)
    assert engine.search_claims() == []


def test_search(engine):
    a = engine.add_claim("A synthetic red beam", subject="beam", predicate="color")
    engine.add_claim("A blue synthetic beam", subject="other")
    assert len(engine.search_claims("synthetic beam")) == 2
    assert len(engine.search_claims("synthetic red", exact_phrase=True)) == 1
    assert (
        len(engine.search_claims(subject="beam", predicate="color", review_status="NEEDS_REVIEW"))
        == 1
    )
    assert engine.search_claims("' OR 1=1; DROP TABLE claims; --") == []
    assert engine.inspect_claim(a["id"])["original_statement"]
    engine.fts = False
    assert len(engine.search_claims("synthetic red", exact_phrase=True)) == 1


@pytest.mark.parametrize("path", ["../outside", "/etc/passwd", "link", "directory", "missing"])
def test_unsafe_files(engine, tmp_path, path):
    (tmp_path / "link").symlink_to("/etc/passwd")
    (tmp_path / "directory").mkdir()
    with pytest.raises((ValueError, OSError)):
        engine.register_source("unsafe", file_path=path)
    assert engine.export_evidence()["sources"] == []


def test_symlink_directory(engine, tmp_path):
    (tmp_path / "escape").symlink_to("/tmp", target_is_directory=True)
    with pytest.raises((ValueError, OSError)):
        engine.register_source("unsafe", file_path="escape/file")
    with pytest.raises(ValueError):
        OpenTruth(tmp_path, data_dir="../escape")


def test_duplicate_sources_are_separate_immutable_copies(engine, tmp_path):
    (tmp_path / "x").write_text("data")
    a = engine.register_source("a", file_path="x")
    b = engine.register_source("a", file_path="x")
    assert a["id"] != b["id"]
    assert a["sha256"] == b["sha256"]
    assert a["file_reference"] != b["file_reference"]


@pytest.mark.parametrize("identifier", ["bad", str(uuid4()), "'; DROP TABLE claims; --"])
def test_invalid_identifiers(engine, identifier):
    with pytest.raises(ValueError):
        engine.inspect_claim(identifier)


def test_foreign_key_and_review_validation(engine):
    a = engine.add_claim("a")
    with pytest.raises(ValueError):
        engine.link_evidence(a["id"], str(uuid4()), "SUPPORTS", "p1", "x", "tester")
    for decision, reason, actor in [
        ("TRUE", "reason", "a"),
        ("REJECTED", "", "a"),
        ("ACCEPTED_FOR_USE", "reason", ""),
    ]:
        with pytest.raises(ValueError):
            engine.review_claim(a["id"], decision, reason, actor)
    assert engine.db.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_corrupt_and_newer_database(tmp_path):
    directory = tmp_path / ".opentruth"
    directory.mkdir()
    path = directory / "evidence.sqlite3"
    path.write_bytes(b"not a database")
    with pytest.raises(sqlite3.DatabaseError):
        OpenTruth(tmp_path)
    path.unlink()
    db = sqlite3.connect(path)
    db.execute("PRAGMA user_version=999")
    db.close()
    with pytest.raises(ValueError, match="newer"):
        OpenTruth(tmp_path)


@pytest.mark.parametrize(
    "value,unit,context,status",
    [
        (1, "m", {"method": "A"}, "NO_DETECTED_CONFLICT"),
        (100, "cm", {"method": "A"}, "NO_DETECTED_CONFLICT"),
        (2, "m", {"method": "A"}, "POTENTIAL_CONFLICT"),
        (2, "m", {"method": "B"}, "INSUFFICIENT_COMPARABILITY"),
        (2, "m", {}, "INSUFFICIENT_COMPARABILITY"),
        (1, "kg", {"method": "A"}, "INSUFFICIENT_COMPARABILITY"),
        (1, None, {"method": "A"}, "INSUFFICIENT_COMPARABILITY"),
        ("qualitative", "m", {"method": "A"}, "NOT_EVALUATED"),
        (1.0001, "m", {"method": "A"}, "NO_DETECTED_CONFLICT"),
    ],
)
def test_scientific_comparisons(engine, value, unit, context, status):
    a = engine.add_claim(
        "a", subject="beam", predicate="length", value=1, unit="m", context={"method": "A"}
    )
    b = engine.add_claim(
        "b", subject="beam", predicate="length", value=value, unit=unit, context=context
    )
    assert compare(a, b, abs_tol=0.001)["status"] == status
    assert engine.check_conflicts(a["id"], abs_tol=0.001)[0]["status"] == status
    assert engine.inspect_claim(a["id"])["potential_conflicts"]


@pytest.mark.parametrize("tolerance", [-1, float("nan"), float("inf")])
def test_bad_tolerance(engine, tolerance):
    a = engine.add_claim("a", subject="x", predicate="p")
    b = engine.add_claim("b", subject="x", predicate="p")
    with pytest.raises(ValueError):
        compare(a, b, abs_tol=tolerance)


def test_examples(tmp_path):
    from examples.scenarios import run

    assert run(tmp_path)["synthetic"] is True


def test_file_size_limit_and_fifo(engine, tmp_path):
    import os

    oversized = tmp_path / "oversized"
    with oversized.open("wb") as file:
        file.truncate(20 * 1024 * 1024 + 1)
    with pytest.raises(ValueError):
        engine.register_source("too big", file_path="oversized")
    os.mkfifo(tmp_path / "fifo")
    with pytest.raises(ValueError):
        engine.register_source("not regular", file_path="fifo")
    assert list(engine.files.iterdir()) == []


def test_conflicting_evidence_and_repeated_reviews(engine):
    a = engine.add_claim("synthetic")
    for relation in ("SUPPORTS", "CONTRADICTS"):
        source = engine.register_source("synthetic")
        engine.link_evidence(a["id"], source["id"], relation, "p1", "synthetic", "tester")
    assert engine.inspect_claim(a["id"])["evidence_status"] == "CONFLICTING_REGISTERED_EVIDENCE"
    for decision in ("REJECTED", "NEEDS_REVIEW", "INCONCLUSIVE"):
        engine.review_claim(a["id"], decision, "synthetic reason", "tester")
    events = [e for e in engine.get_claim_history(a["id"]) if e["action"] == "HUMAN_REVIEW"]
    assert len(events) == 3
    assert events[0]["details"]["decision"] == "REJECTED"


def test_empty_collection_tolerance_validation(engine):
    a = engine.add_claim("synthetic")
    with pytest.raises(ValueError):
        engine.check_conflicts(a["id"], abs_tol=-1)


def test_symlink_storage_rejected(tmp_path):
    internal = tmp_path / "internal"
    internal.mkdir()
    (tmp_path / ".opentruth").symlink_to(internal, target_is_directory=True)
    with pytest.raises(ValueError):
        OpenTruth(tmp_path)


def test_no_mutation_after_failed_revision(engine):
    a = engine.add_claim("original")
    with pytest.raises(ValueError):
        engine.revise_claim(a["id"], "reason", extra="unknown")
    assert engine.inspect_claim(a["id"])["original_statement"] == "original"
    assert len(engine.get_claim_history(a["id"])) == 1
