"""Small deterministic comparison rule set; no semantic inference."""

import math

from .contexts import context_warnings

UNITS = {
    "s": ("time", 1),
    "min": ("time", 60),
    "h": ("time", 3600),
    "mm": ("length", 0.001),
    "cm": ("length", 0.01),
    "m": ("length", 1),
    "mg": ("mass", 0.001),
    "g": ("mass", 1),
    "kg": ("mass", 1000),
}


def validate_tolerances(abs_tol, rel_tol):
    if not all(math.isfinite(x) and x >= 0 for x in (abs_tol, rel_tol)):
        raise ValueError("Tolerances must be finite and nonnegative")


def compare(a, b, abs_tol=0.0, rel_tol=1e-9):
    validate_tolerances(abs_tol, rel_tol)
    details = {}

    def result(status, reason):
        return {
            "claim_ids": [a["id"], b["id"]],
            "status": status,
            "reason": reason,
            "abs_tol": abs_tol,
            "rel_tol": rel_tol,
            "comparison": details,
            "inputs": [
                {
                    key: claim.get(key)
                    for key in (
                        "id",
                        "original_statement",
                        "subject",
                        "predicate",
                        "context",
                        "context_template",
                        "value",
                        "unit",
                    )
                }
                for claim in (a, b)
            ],
        }

    if (
        not a["subject"]
        or not a["predicate"]
        or (a["subject"], a["predicate"]) != (b["subject"], b["predicate"])
    ):
        return result("INSUFFICIENT_COMPARABILITY", "Missing or different subject/property")
    if not a["context"] or not b["context"]:
        return result("INSUFFICIENT_COMPARABILITY", "Explicit context is required")
    warnings = [context_warnings(c["context"], c.get("context_template")) for c in (a, b)]
    if any(warnings) or a.get("context_template") != b.get("context_template"):
        details["context_warnings"] = warnings
        return result("INSUFFICIENT_COMPARABILITY", "Incomplete or different context templates")
    if a["context"] != b["context"]:
        return result("INSUFFICIENT_COMPARABILITY", "Registered contexts differ")
    x, y = a["value"], b["value"]
    if not isinstance(x, (float, int)) or not isinstance(y, (float, int)):
        return result("NOT_EVALUATED", "Only numeric comparisons are implemented")
    u, v = a["unit"], b["unit"]
    factor = 1
    if u is None or v is None:
        return result(
            "INSUFFICIENT_COMPARABILITY", "Explicit units required (use '1' for dimensionless)"
        )
    if u != v:
        if u not in UNITS or v not in UNITS or UNITS[u][0] != UNITS[v][0]:
            return result("INSUFFICIENT_COMPARABILITY", "Incompatible or unsupported units")
        factor = UNITS[v][1] / UNITS[u][1]
        y = y * factor
    if not math.isfinite(y):
        return result("NOT_EVALUATED", "Unit conversion exceeds finite numeric range")
    difference = abs(x - y)
    relative_threshold = rel_tol * max(abs(x), abs(y))
    details.update(
        normalized_values=[x, y],
        comparison_unit=u,
        conversion_factor=factor,
        absolute_difference=difference if math.isfinite(difference) else "OUT_OF_RANGE",
        absolute_tolerance=abs_tol,
        relative_tolerance=rel_tol,
        allowed_difference=(
            max(abs_tol, relative_threshold)
            if math.isfinite(relative_threshold)
            else "OUT_OF_RANGE"
        ),
        rule="abs(a-b) <= max(abs_tol, rel_tol * max(abs(a), abs(b)))",
    )
    if math.isclose(x, y, abs_tol=abs_tol, rel_tol=rel_tol):
        return result(
            "NO_DETECTED_CONFLICT", "Values agree within tolerances in first claim's unit"
        )
    return result(
        "POTENTIAL_CONFLICT",
        "Numeric values differ beyond tolerances in matching registered context",
    )
