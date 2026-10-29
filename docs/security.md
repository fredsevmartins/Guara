# Security model

Use a dedicated trusted workspace, not a home directory containing secrets. Source paths must be
relative, contain no `..`, resolve within that workspace, and have no symlink components. Copied
files have generated UUID names, exclusive creation, SHA-256 hashes, and a 20 MiB limit. Records
have a 100 KB serialized size limit; statements and excerpts have a 20,000 character limit.
File copying uses directory descriptors and O_NOFOLLOW to reject symlink replacement races on POSIX.
Platforms lacking these primitives reject local file copies. Storage directories remain trusted.
SQL values are parameterized; dynamic table names are internal constants only. FTS expressions
quote input tokens rather than accepting raw FTS query syntax. No URLs are fetched and no source
content is executed. MCP operational errors hide filesystem paths. Core Python exceptions may
contain local details and should not be forwarded to untrusted clients.

Single trusted OS user only: no authentication, encryption, multi-tenant isolation, or tamper-evident
logs. Anyone with database write access can modify history. Avoid concurrent untrusted filesystem
mutation. Protect backups and exports; they include evidence text, authors, and actor strings.
See SECURITY.md for reporting. Tests cover traversal, symlink escapes, malformed input, corruption,
oversized records, invalid IDs, SQL injection strings, and independent source copies.
