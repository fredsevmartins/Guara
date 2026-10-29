import json

import pytest
from test_interfaces import cli

from opentruth import OpenTruth
from opentruth.conflicts import compare


def test_explained_conversion_and_threshold(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim(
        "SYNTHETIC 1m",
        subject="beam",
        predicate="length",
        value=1,
        unit="m",
        context={"method": "synthetic"},
    )
    b = dict(a, value=125, unit="cm")
    result = compare(a, b, abs_tol=0.25, rel_tol=0)
    details = result["comparison"]
    assert result["status"] == "NO_DETECTED_CONFLICT"
    assert details["normalized_values"] == [1, 1.25]
    assert details["comparison_unit"] == "m"
    assert details["conversion_factor"] == 0.01
    assert details["absolute_difference"] == details["allowed_difference"] == 0.25
    app.close()


def test_extreme_difference_remains_json_serializable(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim(
        "SYNTHETIC",
        subject="x",
        predicate="y",
        value=1e308,
        unit="1",
        context={"method": "synthetic"},
    )
    b = dict(a, value=-1e308)
    result = compare(a, b)
    assert result["status"] == "POTENTIAL_CONFLICT"
    assert result["comparison"]["absolute_difference"] == "OUT_OF_RANGE"
    json.dumps(result, allow_nan=False)
    app.close()


@pytest.mark.parametrize("template", ["engineering", "experiment", "study"])
def test_context_checklists_warn_and_prevent_unsupported_comparison(tmp_path, template):
    from opentruth.contexts import TEMPLATES

    app = OpenTruth(tmp_path)
    a = app.add_claim(
        "SYNTHETIC",
        subject="x",
        predicate="y",
        value=1,
        unit="1",
        context={"method": "synthetic"},
        context_template=template,
    )
    assert a["context_warnings"]
    assert compare(a, dict(a, value=2))["status"] == "INSUFFICIENT_COMPARABILITY"
    complete = {field: "synthetic" for field in TEMPLATES[template]["fields"]}
    revised = app.revise_claim(a["id"], "complete synthetic context", context=complete)
    assert not app.inspect_claim(a["id"])["context_warnings"]
    assert compare(revised, dict(revised, value=2))["status"] == "POTENTIAL_CONFLICT"
    app.close()


def test_cli_convenience_readable_backup_and_restore(tmp_path):
    added = cli(
        tmp_path,
        "claim",
        "add",
        "SYNTHETIC beam",
        "--value",
        "1",
        "--unit",
        "m",
        "--context-template",
        "engineering",
    )
    assert added.returncode == 0, added.stderr
    record = json.loads(added.stdout)
    assert record["context_warnings"]
    human = cli(tmp_path, "--format", "text", "claim", "inspect", record["id"])
    assert human.returncode == 0
    assert "SYNTHETIC beam" in human.stdout and "Warning:" in human.stdout
    assert cli(tmp_path, "backup", "copy.zip").returncode == 0
    restore = cli(tmp_path, "restore", "copy.zip", "--data-dir", "copy")
    assert restore.returncode == 0, restore.stderr
    assert cli(tmp_path, "restore", "copy.zip", "--data-dir", "copy").returncode == 1
    assert cli(tmp_path, "context", "templates", "engineering").returncode == 0
    assert (
        cli(
            tmp_path, "claim", "add", "SYNTHETIC", "--json", '{"original_statement":"duplicate"}'
        ).returncode
        == 1
    )


def test_cli_integrity_failure_exit_code(tmp_path):
    (tmp_path / "input").write_bytes(b"SYNTHETIC")
    result = cli(tmp_path, "source", "add", "SYNTHETIC source", "--file", "input")
    assert result.returncode == 0, result.stderr
    source = json.loads(result.stdout)
    (tmp_path / ".opentruth" / source["file_reference"]).unlink()
    report = cli(tmp_path, "source", "verify", source["id"])
    assert report.returncode == 1
    assert json.loads(report.stdout)["sources"][0]["integrity_status"] == "MISSING"


def test_bad_restore_does_not_initialize_live_store(tmp_path):
    (tmp_path / "bad.zip").write_bytes(b"SYNTHETIC not a zip")
    result = cli(tmp_path, "restore", "bad.zip")
    assert result.returncode == 1
    assert json.loads(result.stderr)["error"] == "INVALID_INPUT_OR_STORAGE"
    assert "Traceback" not in result.stderr
    assert not (tmp_path / ".opentruth").exists()
