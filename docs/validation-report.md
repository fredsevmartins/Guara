# v0.1.1 implementation validation

Validated on 2026-10-29 with Python 3.12.14/Linux, SQLite 3.53.1 (FTS5 available), MCP SDK 1.30.0,
and Pydantic 2.14.1. This report distinguishes locally executed checks from configured remote jobs.

| Check | Result |
|---|---|
| Editable installation with development dependencies | Passed |
| `python -m pytest -q` | 81 passed, 0 failed, 0 skipped |
| Real MCP subprocess/client integration | Passed; all ten tools called, valid/invalid inputs exercised |
| `ruff check .` and `git diff --check` | Passed |
| Four assertion-checked synthetic scenarios | Passed |
| sdist and wheel builds | Passed |
| Wheel installed into a fresh venv outside the checkout | Passed; evidence workflow, backup, restore, persistence |
| Dependency consistency (`pip check`) | Passed |
| CI and release workflow YAML syntax | Parsed successfully |
| Python 3.11–3.13 on Linux/macOS/Windows | Configured in CI; remote results not confirmed locally |
| GitHub Actions and Release status | API access blocked at the proxy; do not infer success from a tag push |
| Coverage | Not measured |
| ChatGPT connectivity | Not verified; local stdio MCP only |

The suite covers original wording, revisions, provenance, source checksums, relationship histories,
review attribution, exports, SQLite persistence, search, numerical contexts and unit conversions,
tolerance boundaries, malformed inputs, corrupt/newer databases, SQL injection strings, filesystem
traversal/symlinks, oversized/FIFO source files, collision-safe copying, CLI exit codes, and MCP.

New tests cover complete source-backed backup round trips, metadata-only portable backup/restore,
changed/missing/unsafe stored files, source verification separation, refusal to overwrite stores or
archives, byte tampering, forged manifest membership, archive traversal, duplicate members, size
limits, corrupted database snapshots, database/source hash disagreement, safe restore failures,
comparison explanations, finite JSON output at extreme numerical ranges, optional context
checklists, readable CLI output, convenience arguments, and the platform-specific file-ingestion
contract. Windows CI intentionally runs metadata/CLI/MCP tests instead of POSIX-only file-ingestion
and filesystem-primitive tests. It does not claim equivalent local-file copying support.

Source directory mutation, restore, and simultaneous restores require a trusted single-user
workspace. The backup format is bounded and checksummed, not encrypted or authenticated. These
checks validate software behavior; they do not establish scientific reliability or comprehensive
security. Earlier Mermaid syntax parsing succeeded for six diagrams; no diagrams changed in
v0.1.1. Visual rendering remains unverified due to Chromium's local-file policy.

The command sandbox restricts MCP subprocess communication and network access. The supported
escalated command mode was used for the successful suite, installation, and builds, retaining proxy,
TLS, and package verification. `api.github.com` remains denied at proxy CONNECT (HTTP 403). A saved
network draft is not an applied policy. Publication outcomes are reported separately; the new
GitHub release workflow is gated on its own CI results and uses least-privilege job permissions.
