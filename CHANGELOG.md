# Changelog

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
