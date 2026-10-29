"""Entirely SYNTHETIC scenarios, executable without an LLM or network."""

import json
import tempfile

from opentruth import OpenTruth


def run(workspace):
    engine = OpenTruth(workspace)

    def numeric(value, context, unit="h", subject="Fictional Compound X", predicate="half-life"):
        return engine.add_claim(
            f"SYNTHETIC: {subject} {predicate} is {value} {unit}.",
            subject=subject,
            predicate=predicate,
            value=value,
            unit=unit,
            context=context,
            provenance={"synthetic": True},
        )

    # A: Different experimental conditions do not establish a contradiction.
    a = numeric(12, {"population": "synthetic adults", "method": "assay A"})
    numeric(18, {"population": "synthetic juveniles", "method": "assay A"})
    numeric(18, a["context"])
    pharmacokinetic = engine.check_conflicts(a["id"])
    assert {r["status"] for r in pharmacokinetic} == {
        "INSUFFICIENT_COMPARABILITY",
        "POTENTIAL_CONFLICT",
    }
    # B: Conflicting registered evidence, followed by an attributed review.
    b = engine.add_claim("SYNTHETIC: Material Q resists fictional solvent R.")
    for relation in ("SUPPORTS", "CONTRADICTS"):
        source = engine.register_source(
            "SYNTHETIC solvent experiment " + relation, source_type="EXPERIMENT"
        )
        engine.link_evidence(
            b["id"],
            source["id"],
            relation,
            "synthetic table 1",
            "SYNTHETIC observation",
            "synthetic demonstrator",
        )
    engine.review_claim(
        b["id"], "INCONCLUSIVE", "Synthetic findings disagree", "synthetic reviewer"
    )
    changing = engine.inspect_claim(b["id"])
    assert changing["evidence_status"] == "CONFLICTING_REGISTERED_EVIDENCE"
    # C: AI provenance remains explicit; registration never verifies a source.
    c = engine.add_claim(
        "SYNTHETIC: Imaginary alloy Z is self-healing.",
        provenance={"origin": "AI", "synthetic": True},
    )
    assert engine.inspect_claim(c["id"])["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    source = engine.register_source("SYNTHETIC alloy report")
    engine.link_evidence(
        c["id"],
        source["id"],
        "SUPPORTS",
        "section 2",
        "Synthetic assertion",
        "synthetic demonstrator",
    )
    unsupported = engine.inspect_claim(c["id"])
    assert unsupported["evidence"][0]["source"]["verification_status"] == "NOT_EVALUATED"
    # D: Conversion, tolerance, incompatible units, and missing context.
    context = {"method": "synthetic caliper", "conditions": "20 C"}
    d = numeric(1, context, "m", "Synthetic beam", "length")
    numeric(100.01, context, "cm", "Synthetic beam", "length")
    numeric(1, context, "kg", "Synthetic beam", "length")
    numeric(1, {}, "m", "Synthetic beam", "length")
    engineering = engine.check_conflicts(d["id"], abs_tol=0.001)
    assert [r["status"] for r in engineering] == [
        "NO_DETECTED_CONFLICT",
        "INSUFFICIENT_COMPARABILITY",
        "INSUFFICIENT_COMPARABILITY",
    ]
    result = {
        "synthetic": True,
        "pharmacokinetic": pharmacokinetic,
        "changing_evidence": changing["evidence_status"],
        "unsupported_ai": unsupported["evidence_status"],
        "engineering": engineering,
    }
    engine.close()
    return result


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as directory:
        print(json.dumps(run(directory), indent=2))
