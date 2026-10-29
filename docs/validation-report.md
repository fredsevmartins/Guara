# v0.1.2 implementation validation

Validated on 2026-10-29 with Python 3.12.14/Linux, SQLite 3.53.1 (FTS5 available), MCP SDK 1.30.0,
and Pydantic 2.14.1. Local observations and configured remote jobs are distinct.

| Check | Result |
|---|---|
| Full Pytest suite | 95 passed, 0 failed, 0 skipped |
| Real MCP stdio client/server session | All twelve tools exercised, including revision/reassessment |
| Ruff and Git whitespace checks | Passed |
| Four synthetic scenarios and executable tutorial | Passed |
| sdist and wheel builds | Passed |
| Strict Twine metadata check | Both packages passed |
| Independent fresh-venv wheel evidence/backup/restore workflow | Passed |
| Dependency consistency | Passed |
| Historical fixtures included in sdist | Confirmed |
| CI/Release/PyPI workflow YAML | Parsed successfully |
| Cross-platform Python matrix | Configured; remote run results not confirmed |
| GitHub CI/Release status | API still blocked by proxy CONNECT (403) |
| PyPI publication | Not performed; no account credentials/bindings or Trusted Publisher available |
| Coverage | Not measured |

New tests verify bounded/stable pages, no history loading for lightweight search, index query-plan
selection, persistent FTS updates, compact batched conflict audit references, history pagination,
shared-instance thread serialization, cross-process busy errors (Python and CLI), prevention of
backup/restore during another cooperating operation, and OS lock recovery after process termination.
Migration tests copy frozen synthetic workspaces produced by the actual published v0.1.0/v0.1.1
sources. All entity/history payloads, provenance and source hashes survive schema-2 upgrade. Tests
append revisions, back up and restore, verify fixture bytes remain unchanged, restore a real old
archive, and ensure failed index migration preserves schema 1 and its original record.

Earlier tests continue to cover claims, original wording, evidence, review history, source-file
security and checksums, conservative numerical comparisons, context checklists, corrupt/unsafe
archives, source-backed restores, persistence, CLI behavior and JSON serialization.

`python scripts/benchmark.py --claims 5000` generated 5,000 synthetic claims in a temporary store.
One local run observed 0.941 s insertion, 0.00074 s reopening, 0.00151 s for a filtered page of
25 claims, and 0.00149 s for 49 matching comparisons. These are single local observations without
cross-version controls or guaranteed performance. CI uses correctness assertions, not timings.

The Windows CI selection includes metadata/CLI/MCP plus migration/concurrency/portable tests;
secure local source ingestion remains POSIX-only. No local macOS/Windows execution is claimed.
Six unchanged Mermaid sources were previously syntax-checked; visual rendering remains blocked
by Chromium policy. Scientific reliability and comprehensive security are not established by this
software validation. The supported escalated command mode was used for subprocess/network checks
without disabling TLS or package verification. Publication outcomes are reported separately.
