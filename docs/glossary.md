# Glossary

| Term | Meaning in Guara |
| --- | --- |
| Claim | Exact statement plus optional structured measurement, context, and provenance |
| Subject | User-supplied identifier for what is described; no semantic entity resolution occurs |
| Predicate / property | User-supplied measured property, such as `length` |
| Value | Finite numeric measurement or qualitative string; numeric strings remain qualitative |
| Unit | Explicit unit label; `1` denotes a declared dimensionless measurement |
| Context | Extensible dictionary of conditions required by the user's comparison policy |
| Context template | Optional checklist that warns about missing fields and constrains comparisons |
| Provenance | Caller-supplied claim metadata describing origin, such as synthetic or AI-assisted input |
| Source | Registered bibliographic metadata and optional copied workspace-local file |
| Evidence link | Attributed relationship between a source and a particular claim revision |
| Actor | Caller-supplied attribution string, not an authenticated identity |
| Review | Recorded decision about using a claim, distinct from its evidence summary |
| Revision | Preserved claim snapshot; claim correction creates another revision |
| Audit event | Ordered record of an operation, accessible through the API; not tamper-proof |
| Conflict candidate | Another numerical claim selected by declared subject/property; it still requires comparability checks |
| Workspace | Existing authorized directory containing the data store and allowed source/backup paths |
| Data directory | `.opentruth/` by default, holding SQLite and copied sources |
| Export | Complete JSON metadata/reference snapshot, without source bytes or an import mechanism |
| Backup | Validated ZIP archive containing a SQLite snapshot and registered source bytes |
| MCP | Model Context Protocol; Guara implements twelve local stdio tools through the Python SDK |
| Integrity | Agreement between stored bytes and a recorded hash, not proof of scientific quality |

Guara is the product/repository name. `opentruth` remains the Python distribution and CLI command;
`OpenTruth` remains the Python class. See [naming and compatibility](repository-name.md).
