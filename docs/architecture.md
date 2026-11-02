# Architecture

`models.py` validates inputs using Pydantic. `engine.py` owns transactional operations;
`database.py` initializes the SQLite schema; `conflicts.py` contains deterministic comparisons.
Concern modules expose the same methods as unbound functions taking an engine first.
`cli.py` and `mcp_server.py` share this engine. No HTTP listener is started.

State lives under `.opentruth/` in the configured workspace: `evidence.sqlite3` and `files/UUID`.
Processes and runtime credentials are never stored as application state. Close Python API engines
when finished. MCP stdio process exit closes its SQLite connection through OS cleanup.
The single-user engine is synchronous. Its operation lock serializes method calls across threads;
cooperating processes also serialize operations. Multi-call workflows are not atomic, and direct
connection/file access is outside the public API guarantees. See [concurrency](scaling-and-concurrency.md).

See [system architecture](workflows/system-architecture.md).
