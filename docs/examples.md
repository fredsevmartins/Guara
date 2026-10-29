# Fully synthetic demonstrations

From the checkout root after installation:

```sh
python -m examples.scenarios
python -m pytest tests/test_engine.py -k examples
```

All inputs live in `examples/scenarios.py`. One command runs four independent stories in a temporary
workspace and prints JSON with `synthetic: true`. Assertions fail if expected outcomes change.

| Scenario | Inputs | Expected behavior |
|---|---|---|
| Pharmacokinetics | Fictional compound half-life 12 vs 18 h; adults vs juveniles, then matching context | INSUFFICIENT_COMPARABILITY for different contexts; POTENTIAL_CONFLICT for matching context |
| Changing evidence | Fictional solvent experiment with support and contradiction, followed by human INCONCLUSIVE review | CONFLICTING_REGISTERED_EVIDENCE; chronological audit events |
| Unsupported AI | Fictional self-healing alloy assertion, AI provenance, then a synthetic support link | Initially INSUFFICIENT_EVIDENCE; later registered support, source still NOT_EVALUATED |
| Engineering | Synthetic beam 1 m vs 100.01 cm, abs_tol=.001 m; kg and missing-context comparisons | NO_DETECTED_CONFLICT after conversion/tolerance; remaining comparisons insufficient |

These examples are software demonstrations, not scientific evidence or medical recommendations.
