# Contributing to Guara

Guara accepts focused bug fixes, documentation improvements, synthetic examples, and proposals
for evidence/comparison rules. Start with an existing issue or open one describing the concrete
problem. See the [code of conduct](CODE_OF_CONDUCT.md) and [support routes](docs/support.md).

## Set up a development environment

Fork the repository if you do not have write access, then clone your fork. From a checkout:

```sh
python -m venv .venv
```

Activate with `. .venv/bin/activate` on a POSIX shell, `.\.venv\Scripts\Activate.ps1` in
PowerShell, or `.venv\Scripts\activate.bat` in Command Prompt. Then:

```sh
python -m pip install -e ".[dev]"
git switch -c fix/describe-the-change
```

Requires Python 3.11+. CI covers 3.11–3.13 on Linux/macOS/Windows. Secure local source ingestion
is POSIX-only; Windows runs the portable subset. See [platform support](docs/platforms-and-releases.md).

## Make a reviewable change

1. Describe the trigger, expected behavior, and affected interface.
2. For a bug fix, add a regression that fails before the fix and passes after it.
3. Preserve exact statements, historical records, revision-bound evidence, and audit attribution.
4. Update the relevant documentation and add an entry under `Unreleased` in `CHANGELOG.md`.
5. Explain compatibility implications and validation in the pull request.

Use synthetic/public data only. Never commit private evidence, credentials, patient information,
a personal `.opentruth` store, virtual environments, or local exports/backups. Frozen synthetic
migration fixtures are intentional exceptions maintained with their expected data and checksums.
Avoid adding generated release binaries for routine changes; current downloads are built by Actions.

## Validate the change

```sh
python -m pytest
ruff check .
python scripts/check_docs.py
python -m examples.scenarios
python -m examples.tutorial
python -m build
python scripts/prepare_release.py
python scripts/wheel_smoke.py
```

The wheel test creates a fresh environment, downloads dependencies, and exercises the installed
API/CLI outside the checkout. Initial dependency installation and wheel smoke tests require
registry access. Other local runtime operations are offline. Run focused regressions while
iterating, then the relevant complete checks before submitting. CI is the authority for supported
platform combinations that you did not execute locally; do not claim unrun environments passed.

| Area | Main regression suites |
| --- | --- |
| Claims, history, evidence, comparison boundaries | `tests/test_engine.py`, `tests/test_improvements.py` |
| CLI full lifecycle, atomic failures, Unicode output | `tests/test_cli_workflows.py` |
| MCP interoperability | `tests/test_interfaces.py` (real stdio session) |
| Backup/restore, path safety, integrity | `tests/test_backup_integrity.py`, `tests/test_portable.py` |
| Pagination, concurrency/crash recovery, migration | `tests/test_scaling_migration.py` |
| Connection cleanup and installed version | `tests/test_usability.py` |
| Release versions, archive boundaries, bundle/checksums | `tests/test_release_bundle.py` |

For example: `python -m pytest tests/test_cli_workflows.py` or
`python -m pytest tests/test_interfaces.py -k real_mcp`. Documentation-only changes should validate
local links and execute affected examples; they do not need a runtime regression that merely
mirrors wording. Build the source distribution when adding documentation/media to verify inclusion.

## Scientific and storage changes

New deterministic rules must describe dimensions, conversion factors, required context,
uncertainties, and tolerance policy. Test compatible, incompatible, missing-context, overflow,
and boundary cases. Do not interpret registered support as truth, weaken conservative statuses,
or conflate review decisions with deterministic checks. Keep optional AI assistance distinct.

Migrations must preserve evidence and attribution, be transactional, and include legacy fixture
and failed-migration tests. Explain upgrade/rollback implications. Never modify schema markers
without the matching migration or rewrite old records to conceal discrepancies.

## Documentation and pull requests

Keep the main technical documentation in English; update the Portuguese onboarding when its
instructions change. Use real CLI/API names, mark placeholders, label synthetic examples, and
include expected results. Link new guides from `docs/README.md`. Make source-local links relative;
use absolute tagged links where release notes will also render outside their source directory.

Open a focused pull request with the [template](.github/PULL_REQUEST_TEMPLATE.md). Include the
problem/result, commands actually run and their results, scientific assumptions if relevant, and
any remaining limitations. Maintainer review decides acceptance; no review-time guarantee is made.
Version bumps, tags, release publication, and any PyPI publication are maintainer actions described
in the [release guide](docs/releasing.md).
