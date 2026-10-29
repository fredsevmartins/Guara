# Changelog

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
