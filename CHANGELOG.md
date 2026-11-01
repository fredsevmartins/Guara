# Changelog

## 0.1.3 — 2026-11-02

- Renamed the product and repository to Guara, retaining the `opentruth` Python/CLI/storage interfaces.
- Reorganized documentation with a navigation index, platform installation guidance, and Brazilian Portuguese onboarding.
- Added Guará, a Brazilian maned wolf mascot, and citation DOI 10.5281/zenodo.23870405.
- Added `opentruth --version` for installation diagnostics and Python context-manager support for reliable connection cleanup.
- Added local documentation-link validation and expanded isolated wheel checks to cover the installed CLI.
- Added terminal flags for combined search, attributed evidence linking/reassessment, claim correction, human review, and numeric tolerances without JSON wrappers.
- Fixed redirected CLI output to use UTF-8 on Windows, preserving scientific symbols and avoiding false failures after successful saves.
- Added full CLI lifecycle/backup tests and failed-operation atomicity regressions.
- Automated complete release ZIP and checksum generation, archive/version validation tests, and CI-gated publication.
- Included English LinkedIn artwork and GitHub release installation/verification guidance.


## 0.1.2 — 2026-10-29

- Paginated SQL filtering, indexed conflict candidates, optional history loading, persistent FTS triggers.
- Transactional schema-2 index migration with frozen legacy snapshots and older archive tests.
- Cross-process/thread operation locks with bounded waits, busy errors, and OS crash recovery.
- Explicit claim/evidence reassessment through two additional MCP tools.
- Executable synthetic tutorial, reproducible 5,000-claim benchmark, and manual PyPI OIDC workflow.
- Registry publication remains pending maintainer Trusted Publisher configuration.


## 0.1.1 — 2026-10-29

- Complete SQLite/source-file backups and validated restore into an absent data directory.
- Source byte-integrity reports through Python, CLI, and MCP, separate from scientific verification.
- Comparison explanations with unit factors, normalized values, differences, and thresholds.
- Optional engineering, experiment, and study context checklists with missing-field warnings.
- Convenience CLI arguments and readable output while retaining JSON automation compatibility.
- Linux/macOS/Windows CI matrix, isolated wheel smoke tests, and gated GitHub Release publication.
- Document POSIX-only secure local source ingestion and the Windows metadata workflow.


## 0.1.0 — 2026-10-29

Initial evidence-memory implementation: SQLite claims, source copies/checksums, explicit evidence
links, revisions, human reviews, search, conservative numeric conflict candidates, JSON export,
CLI, official-SDK stdio MCP server, synthetic demonstrations, and tests.

Release hardening: evidence assessments are bound to claim revisions; comparison records preserve
inputs; unit conversion avoids intermediate overflow. Boolean measurements, blank source titles,
and blank evidence assessments are rejected. Review attribution is optional without inventing
identities; acceptance/rejection require reasons. Expanded regression tests and documentation.
Source identifier collisions preserve the existing stored file. See
[validation results](docs/validation-report.md) for executed checks and external limitations.
