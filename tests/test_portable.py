"""Portable metadata workflows; secure file ingestion is POSIX-only."""

import os

import pytest

from opentruth import OpenTruth
from opentruth.backup import restore_backup


def test_metadata_revision_backup_restore(tmp_path):
    app = OpenTruth(tmp_path)
    a = app.add_claim("SYNTHETIC original", provenance={"synthetic": True})
    source = app.register_source("SYNTHETIC metadata")
    app.link_evidence(a["id"], source["id"], "SUPPORTS", "p1", "SYNTHETIC", "tester")
    app.revise_claim(a["id"], "SYNTHETIC revision", original_statement="SYNTHETIC revised")
    app.review_claim(a["id"], "INCONCLUSIVE")
    app.backup("portable.zip")
    app.close()
    restore_backup(tmp_path, "portable.zip", "copy")
    restored = OpenTruth(tmp_path, "copy")
    record = restored.inspect_claim(a["id"])
    assert record["original_statement"] == "SYNTHETIC revised"
    assert record["revisions"][0]["original_statement"] == "SYNTHETIC original"
    assert record["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert restored.verify_sources()["ok"]
    restored.close()


def test_file_ingestion_platform_contract(tmp_path):
    app = OpenTruth(tmp_path)
    (tmp_path / "input").write_bytes(b"SYNTHETIC")
    if hasattr(os, "O_NOFOLLOW") and os.open in os.supports_dir_fd:
        app.register_source("SYNTHETIC", file_path="input")
        assert app.verify_sources()["sources"][0]["integrity_status"] == "INTACT"
    else:
        with pytest.raises(ValueError, match="not supported"):
            app.register_source("SYNTHETIC", file_path="input")
    app.close()
