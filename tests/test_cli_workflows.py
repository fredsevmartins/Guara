"""End-to-end CLI lifecycle, failed-operation atomicity and search/tolerance boundaries."""

import json

import pytest
from test_interfaces import cli

from opentruth import OpenTruth


def success(workspace, *args):
    result = cli(workspace, *args)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


def test_full_attributed_cli_lifecycle_survives_backup_restore(tmp_path):
    original = "SYNTHETIC: viga α mede 1 m — revisão."
    revised = "SYNTHETIC: viga α mede 2 m — correção."
    claim = success(
        tmp_path, "claim", "add", original, "--subject", "beam", "--predicate", "length",
        "--value", "1", "--unit", "m", "--actor", "recorder",
    )
    source = success(tmp_path, "source", "add", "SYNTHETIC notebook", "--type", "EXPERIMENT")
    link = success(
        tmp_path, "evidence", "link", claim["id"], source["id"], "--relationship", "SUPPORTS",
        "--location", "table 1", "--excerpt", "SYNTHETIC: 1 m", "--actor", "assessor one",
    )
    assert success(tmp_path, "claim", "inspect", claim["id"])["evidence_status"] == (
        "SUPPORTED_BY_REGISTERED_EVIDENCE"
    )
    success(
        tmp_path, "review", claim["id"], "--decision", "ACCEPTED_FOR_USE", "--reason",
        "SYNTHETIC permitted use", "--actor", "reviewer",
    )
    success(
        tmp_path, "claim", "revise", claim["id"], "--statement", revised, "--value", "2",
        "--reason", "SYNTHETIC correction", "--actor", "editor",
    )
    stale = success(tmp_path, "claim", "inspect", claim["id"])
    assert stale["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert stale["review_status"] == "NEEDS_REVIEW"
    success(
        tmp_path, "evidence", "revise", link["id"], "--relationship", "CONTRADICTS",
        "--location", "table 1", "--excerpt", "SYNTHETIC: notebook still says 1 m",
        "--reason", "SYNTHETIC reassessment", "--actor", "assessor two",
    )
    history = success(tmp_path, "history", claim["id"])
    assert [event["actor"] for event in history] == [
        "recorder", "assessor one", "reviewer", "editor", "assessor two",
    ]
    success(tmp_path, "backup", "lifecycle.zip")
    success(tmp_path, "restore", "lifecycle.zip", "--data-dir", "restored")
    with OpenTruth(tmp_path, "restored") as restored:
        record = restored.inspect_claim(claim["id"])
        assert record["original_statement"] == revised
        assert record["revisions"][0]["original_statement"] == original
        assert record["evidence_status"] == "CONTRADICTED_BY_REGISTERED_EVIDENCE"
        assert restored.get_claim_history(claim["id"]) == history


@pytest.mark.parametrize(
    "arguments",
    [
        ["claim", "revise", "CLAIM", "--value", "2", "--reason", " "],
        ["claim", "revise", "CLAIM", "--value", "2", "--reason", "correction", "--json", '{"value":3}'],
        ["review", "CLAIM", "--decision", "REJECTED", "--reason", " "],
        ["evidence", "revise", "LINK", "--reason", "reassess", "--actor", " "],
        ["evidence", "link", "CLAIM", "SOURCE", "--relationship", "SUPPORTS", "--location", " ",
         "--excerpt", "SYNTHETIC", "--actor", "tester"],
        ["claim", "list", "--query", "beam", "--json", '{"query":"other"}'],
    ],
)
def test_rejected_cli_operations_do_not_change_claim_or_audit_history(tmp_path, arguments):
    with OpenTruth(tmp_path) as app:
        claim = app.add_claim("SYNTHETIC beam")
        source = app.register_source("SYNTHETIC source")
        link = app.link_evidence(claim["id"], source["id"], "SUPPORTS", "p1", "SYNTHETIC", "tester")
        before = app.inspect_claim(claim["id"])
        history = app.get_claim_history(claim["id"])
    identifiers = {"CLAIM": claim["id"], "SOURCE": source["id"], "LINK": link["id"]}
    result = cli(tmp_path, *(identifiers.get(arg, arg) for arg in arguments))
    assert result.returncode == 1
    assert not result.stdout
    assert json.loads(result.stderr)["error"] == "INVALID_INPUT_OR_STORAGE"
    with OpenTruth(tmp_path) as app:
        assert app.inspect_claim(claim["id"]) == before
        assert app.get_claim_history(claim["id"]) == history


def test_cli_search_combines_filters_phrases_and_pagination_with_json_compatibility(tmp_path):
    with OpenTruth(tmp_path) as app:
        first = app.add_claim("SYNTHETIC red blue one", subject="beam", predicate="color")
        second = app.add_claim("SYNTHETIC red blue two", subject="beam", predicate="color")
        app.add_claim("SYNTHETIC red green blue", subject="beam", predicate="color")
        app.add_claim("SYNTHETIC red blue", subject="other", predicate="color")
        app.review_claim(first["id"], "ACCEPTED_FOR_USE", "SYNTHETIC review")
    filters = ["--query", "red blue", "--exact-phrase", "--subject", "beam", "--predicate", "color"]
    accepted = success(tmp_path, "claim", "list", *filters, "--review-status", "ACCEPTED_FOR_USE")
    assert [record["id"] for record in accepted] == [first["id"]]
    page = success(tmp_path, "claim", "list", *filters, "--limit", "1", "--offset", "1")
    assert [record["id"] for record in page] == [second["id"]]
    assert "history" not in page[0]
    mixed = success(
        tmp_path, "claim", "list", "--query", "red blue", "--exact-phrase", "--json",
        '{"subject":"beam","predicate":"color","review_status":"ACCEPTED_FOR_USE"}',
    )
    assert mixed == accepted


def test_cli_explicit_tolerances_control_numeric_comparison(tmp_path):
    with OpenTruth(tmp_path) as app:
        claim = app.add_claim(
            "SYNTHETIC one", subject="beam", predicate="length", value=1, unit="m",
            context={"method": "synthetic"},
        )
        app.add_claim(
            "SYNTHETIC two", subject="beam", predicate="length", value=1.1, unit="m",
            context={"method": "synthetic"},
        )
    strict = success(tmp_path, "conflicts", "check", claim["id"], "--abs-tol", "0", "--rel-tol", "0")
    tolerant = success(tmp_path, "conflicts", "check", claim["id"], "--abs-tol", "0.2", "--rel-tol", "0")
    assert strict[0]["status"] == "POTENTIAL_CONFLICT"
    assert tolerant[0]["status"] == "NO_DETECTED_CONFLICT"


def test_cli_uses_utf8_even_with_legacy_redirected_stream_encoding(tmp_path):
    import os
    import subprocess
    import sys

    statement = "SYNTHETIC: viga α — revisão e medição."
    environment = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
    command = [sys.executable, "-m", "opentruth.cli", "--workspace", str(tmp_path)]
    added = subprocess.run(
        [*command, "claim", "add", statement], env=environment, capture_output=True, timeout=10, check=False,
    )
    assert added.returncode == 0, added.stderr
    claim = json.loads(added.stdout.decode("utf-8"))
    assert claim["original_statement"] == statement
    inspected = subprocess.run(
        [*command, "--format", "text", "claim", "inspect", claim["id"]],
        env=environment, capture_output=True, timeout=10, check=False,
    )
    assert inspected.returncode == 0, inspected.stderr
    assert statement in inspected.stdout.decode("utf-8")
    with OpenTruth(tmp_path) as app:
        assert len(app.search_claims()) == 1
        assert len(app.get_claim_history(claim["id"])) == 1
