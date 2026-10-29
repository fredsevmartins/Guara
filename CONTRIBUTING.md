# Contributing

Use a branch and a focused pull request. Install `.[dev]`, run pytest, Ruff, package build,
and the four synthetic examples. Include failing-before regression tests for fixes and describe
scientific assumptions. Never use real patient or private evidence in fixtures.

New deterministic comparison rules must document dimensions, conversion factors, required context,
uncertainties, and tolerances. Test compatible, incompatible, missing-context, and boundary cases.
Do not weaken conservative statuses or conflate human/AI judgments with deterministic checks.
Update docs and changelog alongside behavior. Preserve historical records during migrations.
