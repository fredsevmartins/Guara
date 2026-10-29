# Deterministic comparison

Only claims with matching subject and predicate are selected. Missing identifiers or context,
different registered context dictionaries, missing units, or incompatible units yield
INSUFFICIENT_COMPARABILITY. Equal dictionaries are a limited declared-context policy: users must
record all relevant population, conditions, measurement method, time, geography, and domain fields.
Qualitative values yield NOT_EVALUATED. No natural language contradiction inference is performed.

Supported conversions: s/min/h, mm/cm/m, and mg/g/kg. Matching literal units are compared directly;
use `1` for explicitly dimensionless values. Unsupported differing units are not converted.
Numeric strings are treated as qualitative. NaN and infinities are rejected.
Boolean values are rejected rather than converted into 0/1 measurements. Conversion uses a unit
factor ratio to avoid unnecessary intermediate overflow; an out-of-range converted value yields
NOT_EVALUATED, rather than an unreliable comparison.

The second value is converted into the first claim's unit. Python `math.isclose` uses
`abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)`. Defaults: abs_tol=0 and rel_tol=1e-9.
Absolute tolerance is in the first claim's unit; tolerances must be finite and nonnegative.
Agreement yields NO_DETECTED_CONFLICT; disagreement yields POTENTIAL_CONFLICT, never a truth label.
Every check appends timestamped records and a history event. Prior results remain historical after
revisions, not current automatic warnings. Check again to evaluate current claims.
New comparison records include `inputs`: the exact wording, subject, predicate, values, units,
and context used for both claims. These snapshots keep historical results interpretable after
claim revisions. Legacy comparison records lack these snapshots and must not be treated as
evidence of which historical values were compared.


New records expose a `comparison` explanation containing normalized values, comparison unit,
conversion factor (second claim into first claim's unit), absolute difference, applied absolute
and relative tolerances, allowed difference, and the exact rule. If an intermediate difference or
threshold cannot be represented as a finite float, it is marked OUT_OF_RANGE instead of emitting
invalid JSON. Non-numerical/incomparable outcomes do not imply a numerical check was performed.
Optional context checklists are described in [context templates](context-templates.md).
