# v0.1 implementation validation

Validated locally on Python 3.12.14, SQLite, MCP SDK 1.29.0 and Pydantic 2.13.4.

| Check | Result |
|---|---|
| `python -m pip install -e ".[dev]"` | Passed |
| `python -m pytest` | 40 passed, 0 failed, 0 skipped |
| Real MCP subprocess/client integration | Passed, all nine tools called |
| `ruff check .` | Passed |
| `python -m build` | Passed, sdist and wheel |
| Wheel install and independent smoke test | Passed |
| Four synthetic scenarios | Passed |
| Six Mermaid source files | Parsed successfully with Mermaid |
| Visual rendering | BLOCKED: Chromium administrator policy rejects local file navigation |
| GitHub Actions status and README rendering | Not verified: GitHub API returns Forbidden |
| Coverage | Not measured |
| Python 3.11 / 3.13 execution | Configured in CI, not locally executed |
| ChatGPT compatibility | Not verified; no remote bridge provided |

The suite exercises persistence, revisions, source checksums, audit preservation, search,
relationship changes, reviews, exports, deterministic comparisons, contexts, unit conversions,
tolerances, traversal and symlinks, FIFO/oversized file rejection, SQL injection strings,
malformed inputs/UUIDs, oversized records, duplicate source copies, corrupt/newer databases,
CLI exit codes, and real MCP errors and successful calls.

One dependency warning was observed: AnyIO's pytest plugin uses a pytest alias deprecated for
pytest 10. It did not fail validation. The MCP SDK also emits a Pydantic settings warning when
starting; the real stdio session completed successfully.

IMPLEMENTED / TESTED / DOCUMENTED: evidence foundation, Python API, JSON CLI, stdio MCP,
synthetic examples, provenance, and deterministic numeric comparisons. These results do not
validate scientific content or claim comprehensive security. No independent source verification,
semantic reasoning, remote transport, or authenticated multi-user workflows are available.
The README roadmap describes PLANNED capabilities only. Publication status and final commit
are reported separately after verifying the Git remote. No release tag is created while external
rendering and CI checks remain unverified.
