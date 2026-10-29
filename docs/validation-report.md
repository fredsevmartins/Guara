# v0.1.0 implementation validation

Validated on 2026-10-29 with Python 3.12.14, SQLite 3.53.1 (FTS5 available),
MCP SDK 1.30.0, and Pydantic 2.14.1.

| Check | Result |
|---|---|
| Editable installation with development dependencies | Passed |
| `python -m pytest -q` | 52 passed, 0 failed, 0 skipped |
| Real MCP subprocess/client integration | Passed; all nine tools called, valid and invalid inputs exercised |
| `ruff check .` | Passed |
| `python -m examples.scenarios` | Passed; all four synthetic scenarios asserted |
| `python -m build` | Passed; sdist and wheel generated |
| Independent wheel installation and functional smoke test | Passed; source checksum, evidence, revision reassessment, review, export, restart persistence |
| `python -m pip check` | Passed |
| Six Mermaid source files | Parsed with Mermaid 11 and a DOM implementation; sanitization enabled |
| Local diagram visual rendering | Blocked: Chromium policy rejects the CLI's local file navigation |
| GitHub rendering and Actions status | Not verified; API access denied by the network proxy |
| Coverage | Not measured |
| Python 3.11 / 3.13 execution | Configured in CI, not locally executed |
| ChatGPT connectivity | Not verified; no remote bridge provided |

The suite exercises persistence, revisions, source checksums, audit preservation, search,
relationship changes, reviews, exports, deterministic comparisons, contexts, unit conversions,
tolerance boundaries, traversal and symlinks, FIFO/oversized file rejection, SQL injection strings,
malformed inputs/UUIDs, oversized records, duplicate source copies, corrupt/newer databases,
CLI exit codes, and real MCP errors and successful calls.

Release-hardening regressions cover evidence reassessment after claim revision (including legacy
links), comparison input preservation after revision, optional reviewer attribution, boolean
measurement rejection through Python and MCP, blank evidence fields, conversion overflow, and
source identifier collisions without deleting previously stored files.

The restricted command sandbox initially timed out during MCP initialization and blocked network
connections. The supported escalated execution mode allowed the same full suite to pass without
changing tests or disabling verification. GitHub API requests remain blocked at proxy CONNECT
(HTTP 403), even in that mode. The required `api.github.com` domain was added to the environment
configuration draft; saving a draft does not apply the policy or grant repository permissions.

No independent source verification, semantic reasoning, remote transport, or authenticated
multi-user workflows are implemented. These results validate the development workflow, not
scientific content or comprehensive security. The README roadmap contains planned capabilities
only. Git publication and GitHub Release creation are separate operations; neither follows from
local validation. Publication outcomes are reported separately.
