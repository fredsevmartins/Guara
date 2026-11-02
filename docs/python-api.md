# Python API

This reference describes Guara **0.1.3**. Install the distribution named `opentruth`;
import `OpenTruth` from it. The public engine is synchronous and uses a local SQLite store.

## Open and close a workspace

```python
from opentruth import OpenTruth

with OpenTruth(workspace=".", data_dir=".opentruth", lock_timeout=5) as app:
    claim = app.add_claim(
        "SYNTHETIC: beam Q is 1 m long.",
        subject="beam Q",
        predicate="length",
        value=1,
        unit="m",
        context={"method": "synthetic ruler"},
        provenance={"synthetic": True},
        actor="synthetic demonstrator",
    )
    print(app.inspect_claim(claim["id"])["evidence_status"])
    # INSUFFICIENT_EVIDENCE
```

`workspace` must already exist. `data_dir` is workspace-relative and defaults to `.opentruth`.
The constructor initializes a missing store and migrates supported older schemas. Back up before
opening existing evidence with a newer version. `lock_timeout` accepts 0–60 seconds.

A `with` block closes the connection on success and exceptions. Each operation retains its own
transaction; the block does not combine operations into one transaction. Exceptions propagate.
Explicit `app.close()` remains supported. Do not access `app.db` directly as a public API.

## Sources, claims, and evidence

All methods below return JSON-compatible dictionaries or lists. Creation returns generated IDs;
use those IDs for subsequent operations. The UUIDs are identifiers, not content hashes.

| Method | Required arguments | Optional arguments / defaults | Result |
| --- | --- | --- | --- |
| `register_source` | `title` | `actor=None`, `source_type="OTHER"`, `authors=[]`, `doi`, `url`, `publication_date`, `file_path` | Source record |
| `add_claim` | `original_statement` | `actor=None`, `subject`, `predicate`, `value`, `unit`, `context={}`, `context_template`, `provenance={}` | Claim and context warnings |
| `revise_claim` | `claim_id`, `reason` | `actor=None`, changed Claim fields as keyword arguments | Current claim and warnings |
| `link_evidence` | `claim_id`, `source_id`, `relationship`, `source_location`, `excerpt`, `actor` | None | Evidence link |
| `revise_evidence` | `link_id`, `reason` | `relationship`, `source_location`, `excerpt`, `actor` | Revised evidence link |
| `review_claim` | `claim_id`, `decision` | `reason=""`, `actor=None` | Claim with updated review status |

Collections shown as `[]`/`{}` describe per-record defaults, not shared mutable caller arguments.
Optional source metadata defaults to `None` unless indicated. See [field meanings](glossary.md).

Relationships are `SUPPORTS`, `CONTRADICTS`, `RELATED`, and `INCONCLUSIVE`. Review decisions are
`ACCEPTED_FOR_USE`, `NEEDS_REVIEW`, `REJECTED`, and `INCONCLUSIVE`. Acceptance/rejection and all
revisions require nonblank reasons; links require nonblank actor, location, and excerpt.

`revise_evidence` preserves endpoints and applies its assessment to the current claim revision.
In Python, omitted assessment fields, including actor, retain their previous values. Supply an
explicit actor for a new assessor. The MCP reassessment tool requires an explicit actor. Review
attribution can be omitted (`None`); a supplied review actor must be nonblank. Actor strings are
caller-supplied attribution, not authenticated identities.

Unknown model fields, malformed UUIDs, blank statements/titles, Boolean measurements, and nonfinite
numeric measurements fail validation. Numeric strings are qualitative values. Registration does
not deduplicate records. URLs and DOIs are stored metadata; no lookup occurs. Secure local file
ingestion is POSIX-only. See [security](security.md) and [platforms](platforms-and-releases.md).

## Search, inspection, history, and comparisons

| Method | Required arguments | Optional arguments / defaults | Result |
| --- | --- | --- | --- |
| `search_claims` | None | `query=""`, `exact_phrase=False`, `subject=None`, `predicate=None`, `review_status=None`, `limit=100`, `offset=0`, `include_history=False` | List of inspected claims |
| `inspect_claim` | `claim_id` | `include_history=True` | Claim, links with sources, revision number, evidence summary |
| `get_claim_history` | `claim_id` | `limit=None`, `offset=0` | Ordered audit-event list |
| `check_conflicts` | `claim_id` | `abs_tol=0.0`, `rel_tol=1e-9`, `actor=None`, `limit=100`, `offset=0` | List of recorded comparisons |

Search and comparisons accept page sizes 1–1000. Python history defaults to all events; supply a
limit to bound retrieval. CLI history also leaves the limit unset unless provided; MCP history
defaults to 100. Pagination follows insertion order and does not provide a multi-request snapshot.

Search combines filters with AND. FTS5 uses quoted AND tokens, or a quoted whole phrase when
requested. The fallback uses Unicode casefold substring matching; tokenization can differ.
Without history, results omit `revisions`, `history`, and `potential_conflicts`, but still include
registered evidence/source records. Full inspection includes those arrays. No source file bytes
are loaded into search results.

`revision_number` identifies the current revision. Every inspected evidence link has
`applies_to_current_revision`; stale links remain visible but do not contribute to the summary.
See [statuses](statuses.md) and [evidence model](evidence-model.md).

`check_conflicts` is an auditable operation: it writes comparison records and a history event.
Tolerances must be finite and nonnegative; absolute tolerance uses the inspected claim's unit.
Different values require matching declared context and compatible units before comparison.
See [comparison rules](conflict-detection.md). An empty result is an empty candidate page, not a
statement that all possible scientific contradictions have been excluded.

## Export, integrity, backup, and restore

| Method | Arguments | Result |
| --- | --- | --- |
| `export_evidence` | `actor=None` | Complete metadata export; adds an export audit event |
| `verify_sources` | `source_id=None` | Byte-integrity report with `sources`, `ok`, and `scientific_verification` |
| `backup` | `archive_path` | Backup creation report; existing archive is never overwritten |
| `restore_backup` (module function) | `workspace`, `archive_path`, `data_dir=".opentruth"`, `lock_timeout=5` | Restore report; destination must be absent |

```python
from opentruth import OpenTruth
from opentruth.backup import restore_backup

with OpenTruth(".") as app:
    app.backup("snapshot.zip")
restore_backup(".", "snapshot.zip", data_dir="restored-evidence")
with OpenTruth(".", data_dir="restored-evidence") as restored:
    assert restored.verify_sources()["ok"]
```

Run the example with an unused archive/destination name. Backup/restore paths must be
workspace-relative and satisfy the [archive and path limits](backup-and-integrity.md).

Current exports contain `schema_version: 2`, `exported_at`, `files_included: false`, and arrays
`claims`, `sources`, `evidence_links`, `claim_revisions`, `review_events`, and `conflict_records`.
Array order follows insertion order. JSON exports contain references, not source bytes; no JSON
import is implemented. **Database/export schema 2 and backup format 1 are separate versions.**
The backup manifest accepts schema 1–2. See [data model](data-model.md).

## Error handling and concurrency

Catch `opentruth.locking.WorkspaceBusy` when another cooperating operation exceeds the configured
wait. Validation can raise `ValueError` (including Pydantic validation errors); incorrect call
shapes can raise `TypeError`. Storage operations can raise `OSError` or `sqlite3.Error`. Python
exceptions can include local details; avoid forwarding raw errors to untrusted clients.

An engine serializes its operations across threads, and cooperating processes use OS advisory
locks. Multi-call workflows are not atomic: another client can operate between calls. Direct SQL
and concurrent external file mutation are outside these guarantees. See
[concurrency](scaling-and-concurrency.md) and [operations](operations.md).
