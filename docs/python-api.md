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
| add_claim | original_statement | actor, subject, predicate, value, unit, context, provenance |
| revise_claim | claim_id, reason | actor, changed Claim model fields |
| link_evidence | claim_id, source_id, relationship, source_location, excerpt, actor | — |
| revise_evidence | link_id, reason | relationship, source_location, excerpt, actor |
| search_claims | — | query, exact_phrase, subject, predicate, review_status |
| inspect_claim | claim_id | — |
| check_conflicts | claim_id | abs_tol=0, rel_tol=1e-9, actor |
| get_claim_history | claim_id | — |
| review_claim | claim_id, decision, reason, actor | — |
| export_evidence | — | actor |

Review decisions: ACCEPTED_FOR_USE, NEEDS_REVIEW, REJECTED, INCONCLUSIVE. All require a nonblank
reason and actor. Unknown model fields and malformed UUIDs fail validation. Duplicate registration
creates separate IDs (no inferred deduplication). Keyword search uses FTS5 AND tokens; exact phrase
quotes the full phrase. The fallback uses case-insensitive substring checks; tokenization can differ.

Export format: `schema_version: 1`, `exported_at`, `files_included: false`, and arrays named for all
six persisted entity/history tables. IDs and source file references are retained. Order within
history arrays follows insertion order. Export adds its own audit event. Files require a separate
backup; no import is implemented. Entities, activities, and actor attribution are inspired by W3C
PROV terminology, without claiming validated PROV standards compliance.
