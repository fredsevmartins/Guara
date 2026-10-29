# Python API

```python
from opentruth import OpenTruth

app = OpenTruth(workspace=".", data_dir=".opentruth")
claim = app.add_claim(
    "Exact wording",
    subject="x",
    predicate="length",
    value=1,
    unit="m",
    context={"method": "synthetic"},
    provenance={"origin": "user"},
)
app.revise_claim(claim["id"], reason="Clarification", original_statement="New wording")
app.close()
```

| Method | Required arguments | Optional arguments |
|---|---|---|
| register_source | title | actor, source_type, authors, doi, url, publication_date, file_path |
| add_claim | original_statement | actor, subject, predicate, value, unit, context, context_template, provenance |
| revise_claim | claim_id, reason | actor, changed Claim model fields |
| link_evidence | claim_id, source_id, relationship, source_location, excerpt, actor | — |
| revise_evidence | link_id, reason | relationship, source_location, excerpt, actor |
| search_claims | — | query, exact_phrase, subject, predicate, review_status |
| inspect_claim | claim_id | — |
| check_conflicts | claim_id | abs_tol=0, rel_tol=1e-9, actor |
| get_claim_history | claim_id | — |
| review_claim | claim_id, decision | reason, actor |
| export_evidence | — | actor |

Review decisions: ACCEPTED_FOR_USE, NEEDS_REVIEW, REJECTED, INCONCLUSIVE. Acceptance and rejection
require a nonblank reason. Actor attribution is optional; an omitted actor is stored as null,
and a supplied actor must not be blank. No reviewer identity is invented. Evidence links still
require explicit, nonblank actor, location, and excerpt. Boolean measurements are rejected.
Unknown model fields and malformed UUIDs fail validation. Duplicate registration
creates separate IDs (no inferred deduplication). Keyword search uses FTS5 AND tokens; exact phrase
quotes the full phrase. The fallback uses case-insensitive substring checks; tokenization can differ.

Inspection includes `revision_number` and each link's `applies_to_current_revision` flag. See the
[evidence model](evidence-model.md) for reassessment after revisions and legacy record handling.

Export format: `schema_version: 1`, `exported_at`, `files_included: false`, and arrays named for all
six persisted entity/history tables. IDs and source file references are retained. Order within
history arrays follows insertion order. Export adds its own audit event. Files require a separate
backup; no import is implemented. Entities, activities, and actor attribution are inspired by W3C
PROV terminology, without claiming validated PROV standards compliance.


| Additional method | Required arguments | Optional arguments |
|---|---|---|
| verify_sources | — | source_id |
| backup | archive_path | — |

`from opentruth.backup import restore_backup` exposes `restore_backup(workspace, archive_path,
data_dir=".opentruth")`. The target data directory must be absent. See the
[backup format and limits](backup-and-integrity.md). JSON export remains metadata-only; archive
backup additionally includes registered source bytes.


Since v0.1.2, `search_claims` and `check_conflicts` accept `limit=100, offset=0` (limit 1–1000).
Search accepts `include_history=False`; `inspect_claim` accepts `include_history=True` by default.
`get_claim_history` accepts `limit=None, offset=0` in Python (MCP defaults to 100).
`OpenTruth` and `restore_backup` accept `lock_timeout=5` (0–60 seconds). Catch
`opentruth.locking.WorkspaceBusy` to handle another client's active operation. See
[scaling/concurrency](scaling-and-concurrency.md) for compatibility and snapshot limitations.
