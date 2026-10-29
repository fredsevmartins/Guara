"""Executable, entirely synthetic evidence/reassessment/backup tutorial."""

import json
import tempfile

from opentruth import OpenTruth
from opentruth.backup import restore_backup


def run(workspace):
    app = OpenTruth(workspace)
    claim = app.add_claim(
        "SYNTHETIC: beam Q is 1 m long.",
        subject="beam Q",
        predicate="length",
        value=1,
        unit="m",
        context={"method": "synthetic caliper"},
        provenance={"synthetic": True},
    )
    source = app.register_source("SYNTHETIC measurement notebook", source_type="EXPERIMENT")
    link = app.link_evidence(
        claim["id"],
        source["id"],
        "SUPPORTS",
        "table 1",
        "SYNTHETIC: 1 m measured",
        "synthetic demonstrator",
    )
    assert app.inspect_claim(claim["id"])["evidence_status"] == "SUPPORTED_BY_REGISTERED_EVIDENCE"
    app.revise_claim(
        claim["id"],
        "SYNTHETIC transcription correction",
        value=2,
        original_statement="SYNTHETIC: beam Q is 2 m long.",
    )
    assert app.inspect_claim(claim["id"])["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    app.revise_evidence(
        link["id"],
        "SYNTHETIC reassessment of revised claim",
        relationship="CONTRADICTS",
        actor="synthetic demonstrator",
    )
    app.review_claim(claim["id"], "NEEDS_REVIEW", "SYNTHETIC: new measurement needed")
    page = app.search_claims(subject="beam Q", limit=1, offset=0)
    assert len(page) == 1 and "history" not in page[0]
    history = app.get_claim_history(claim["id"], limit=100, offset=0)
    assert len(history) == 5
    assert app.verify_sources()["sources"][0]["integrity_status"] == "NO_LOCAL_FILE"
    app.backup("tutorial.zip")
    app.close()
    restore_backup(workspace, "tutorial.zip", "restored")
    restored = OpenTruth(workspace, "restored")
    record = restored.inspect_claim(claim["id"])
    assert record["evidence_status"] == "CONTRADICTED_BY_REGISTERED_EVIDENCE"
    assert record["revisions"][0]["original_statement"] == "SYNTHETIC: beam Q is 1 m long."
    restored.close()
    return {
        "synthetic": True,
        "evidence_status": record["evidence_status"],
        "history_events": len(history),
        "backup_restored": True,
        "scientific_verification": "NOT_EVALUATED",
    }


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as workspace:
        print(json.dumps(run(workspace), indent=2))
