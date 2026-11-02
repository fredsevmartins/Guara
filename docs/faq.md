# Frequently asked questions

## What is Guara, and why does installation say opentruth?

Guara is the product/repository name. `opentruth` remains the distribution and CLI, `OpenTruth`
remains the Python class, and `.opentruth/` remains the storage directory for compatibility.
See [naming](repository-name.md). The product is a CLI, Python API, and local stdio MCP server;
0.1.3 does not include a browser dashboard.

## Does registered support or acceptance mean a claim is true?

No. Support means a caller recorded a `SUPPORTS` link. Acceptance is a separate review decision
about use. Neither verifies source content, authenticates the actor, or erases contrary evidence.
See [statuses](statuses.md) and [scientific integrity](scientific-integrity.md).

## Are DOIs, URLs, and AI provenance independently verified?

No. Metadata/provenance are caller-supplied. Guara does not fetch DOI/URL content, score reliability,
or turn AI-generated claims into verified facts. A source hash checks stored bytes, not science.

## Does it work offline, and do I need an LLM?

Installed local operations work offline and need no LLM, account, or API key. Initial dependency
installation and isolated wheel-install checks need registry access. Your separate assistant/client
can have its own networking requirements. No remote HTTP MCP transport is supplied.

## Can I use Windows or connect it directly to ChatGPT?

Windows supports metadata, CLI/MCP, and portable backup/restore workflows. Secure ingestion of
new local source files is POSIX-only. The MCP client must be able to launch a local stdio process;
ChatGPT compatibility is not verified. See [platforms](platforms-and-releases.md) and
[MCP integration](mcp-integration.md).

## Why does evidence become insufficient after correcting a claim?

Links refer to a particular revision. Correction preserves the original and resets claim review;
prior assessments no longer contribute until explicitly reassessed. They stay visible in history.
See [evidence model](evidence-model.md).

## Why do different numbers not always generate a potential conflict?

A meaningful deterministic comparison requires matching subject/property, explicit matching
context, compatible units, and finite numeric values. Numeric strings are qualitative. Different
contexts can be scientifically appropriate. See [comparison rules](conflict-detection.md).

## Are all results returned by one search or history call?

Search/comparison pages default to 100, maximum 1000. Python/CLI history is unbounded unless a
limit is supplied; MCP history defaults to 100. Fetch pages with stable filters and data when a
complete traversal matters. Full export is not paginated. See [scaling](scaling-and-concurrency.md).

## Can I import a JSON export or restore over my current database?

No JSON import or merge is implemented. Exports exclude source bytes. A complete backup includes
registered bytes; restore requires an absent destination and does not overwrite live data.
Use a new workspace for normal CLI access to a restored default store. See
[backup/restore](backup-and-integrity.md) and [operations](operations.md).

## Can collaborators share the same writable store?

Cooperating processes serialize operations for one trusted OS user. This is not authenticated
multi-user collaboration, a distributed service, or tamper-proof audit storage. Multi-call
workflows are not atomic, and direct SQL/file edits bypass application guarantees.

## Can I delete, redact, or anonymize records?

There is no supported deletion, selective redaction, or anonymization API in 0.1.3. Revisions preserve
history; they do not erase old text. Review retention and sensitive-data requirements before
recording material. Manage external copies through your normal storage procedures.

## Where do I get help or contribute?

Use [support](support.md) and [contributing](../CONTRIBUTING.md). Report security issues through
[SECURITY.md](../SECURITY.md), not a public evidence attachment. There is no support SLA.
