# Limitations

No autonomous truth determination, qualitative contradiction inference, extraction, embeddings,
source reliability score, external DOI/URL verification, remote fetching, or authenticated review.
No network server by default or verified ChatGPT integration. No JSON-export import, deletion/redaction API, JSON-LD/PROV compliance,
source version monitoring, collaborative access control, or vector search in v0.1.

Context is an open dictionary, not a domain ontology; exact dictionary equality can miss important
confounders. Only finite numeric values are compared. Supported conversions are deliberately small.
Registered evidence summaries ignore quality, strength, independence, and review disposition.
Conflict records describe the state at the time of a check; rerun after revisions.

SQLite supports a trusted local workflow, not authenticated multi-user editing. Search uses
indexed SQL filters and defaults to pages of 100 (maximum 1000); the fallback text matcher can
scan candidates, and evidence inspection/export can still be expensive for large histories.
Pagination is not a cross-request snapshot. Benchmark representative data before scaling. FTS5
and fallback substring tokenization differ. File registration is not a secure multi-tenant file broker.
Future v0.2–v1.0 capabilities in README are PLANNED only.
