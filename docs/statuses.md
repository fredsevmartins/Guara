# Reading statuses and results

Guara exposes separate review, registered-evidence, comparison, source-verification, and
file-integrity states. Interpret each field independently. None authenticates an actor or
establishes scientific truth.

## Claim review: `review_status`

| Value | Meaning | Typical next step |
| --- | --- | --- |
| `NEEDS_REVIEW` | Default on creation and after claim correction | Inspect wording, context, and current evidence |
| `ACCEPTED_FOR_USE` | A caller recorded acceptance with a reason | Check that the use matches that reason |
| `REJECTED` | A caller recorded rejection with a reason | Read the review history before reuse |
| `INCONCLUSIVE` | A caller recorded an unresolved review | Identify missing evidence or context |

A review does not suppress contradictory evidence or change numeric comparison rules.
Evidence links also carry `review_status: NEEDS_REVIEW`; there is no separate link-review endpoint.
`review_claim` updates claim review only.

## Claim inspection: `evidence_status`

Only links assessed against the current claim revision contribute to this summary.

| Value | Registered relationships for the current revision |
| --- | --- |
| `SUPPORTED_BY_REGISTERED_EVIDENCE` | At least one `SUPPORTS` and no `CONTRADICTS` |
| `CONTRADICTED_BY_REGISTERED_EVIDENCE` | At least one `CONTRADICTS` and no `SUPPORTS` |
| `CONFLICTING_REGISTERED_EVIDENCE` | Both `SUPPORTS` and `CONTRADICTS` |
| `INSUFFICIENT_EVIDENCE` | Neither supporting nor contradicting current assessments |

`RELATED` and `INCONCLUSIVE` relationships do not count as support or contradiction. The summary
uses relationship labels, without weighting source quality, independence, or review decisions.
A corrected claim can show insufficient evidence while historical links remain visible with
`applies_to_current_revision: false`. Reassess explicitly; see [evidence model](evidence-model.md).

## Numeric comparison: `status`

| Value | Meaning |
| --- | --- |
| `NO_DETECTED_CONFLICT` | Compared numeric values agree within the supplied tolerances |
| `POTENTIAL_CONFLICT` | Compared numeric values differ beyond those tolerances |
| `INSUFFICIENT_COMPARABILITY` | Context, identifiers, templates, or units prevent comparison |
| `NOT_EVALUATED` | Numeric evaluation was not performed, for example for qualitative values or overflow |

Read `reason`, `inputs`, and `comparison` alongside the status. Results are historical snapshots;
rerun after relevant changes. An empty comparison list means no candidates in that requested page.
It is not a completeness guarantee. See [comparison rules](conflict-detection.md).

## Source verification and local byte integrity

Registered sources retain `verification_status: NOT_EVALUATED`. Integrity reports also state
`scientific_verification: NOT_EVALUATED`, even when every stored file is intact.

| `integrity_status` | Meaning | Action |
| --- | --- | --- |
| `INTACT` | Read bytes match the registered hash | Evaluate scientific content separately |
| `ALTERED` | Read bytes differ from that hash | Preserve the discrepancy and recover trusted bytes or register a new source |
| `MISSING` | Stored file was not found | Locate a verified backup |
| `UNREADABLE_OR_UNSAFE` | A safe permitted read could not be completed | Check permissions/path constraints and preserve the original |
| `NO_LOCAL_FILE` | Metadata-only source | Do not interpret it as a file check |

The report's `ok` is true when all entries are `INTACT` or `NO_LOCAL_FILE`, including an empty
store. It does not mean all sources contain checked local files. On Windows, some missing/unsafe
paths may be classified as `UNREADABLE_OR_UNSAFE` rather than `MISSING` by the fallback reader.
CLI integrity failures exit 1 but still return the report on stdout. See
[backup and integrity](backup-and-integrity.md).
