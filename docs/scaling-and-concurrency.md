# Pagination, indexes, and cooperating clients

## Search and comparisons

Search and conflict checking accept `limit` (default 100, maximum 1000) and `offset` (default 0).
Fetch successive pages until a page contains fewer than `limit` records. Ordering follows claim
insertion order. Offsets are not snapshot cursors: changes to filters/claims between requests can
change page membership. Keep the dataset stable when exporting a complete paginated traversal.

```sh
opentruth claim list --limit 25 --offset 0
opentruth claim list --limit 25 --offset 25 --include-history
opentruth conflicts check CLAIM_UUID --limit 50 --offset 0
opentruth history CLAIM_UUID --limit 25 --offset 0
```

Search returns claim fields, evidence/source references, review status, and evidence summaries.
It omits `history`, `revisions`, and `potential_conflicts` unless `include_history=True` is requested.
Direct `inspect_claim` keeps its full-history default for compatibility and also accepts
`include_history=False`. Python history supports optional pagination (default `limit=None` retains
all events); the MCP history tool defaults to 100. JSON exports remain complete.

SQLite expression indexes select subject/property and review filters. FTS5 queries use the text
index before inspection; the no-FTS fallback preserves Unicode casefold substring matching in a
SQLite function. A one-time FTS rebuild installs transactional insert/update/delete triggers; later
opens reuse the index. Direct external index/schema mutation is unsupported. Conflict batches
record comparison IDs in audit events, avoiding duplication of whole comparison snapshots.

## Concurrent CLI/MCP clients

Operations acquire an exclusive OS advisory lock for the canonical workspace/data-directory pair.
This serializes reads, writes, initialization, source copying, backup, and restore across cooperating
processes; an instance also serializes threads. Multi-step changes retain SQLite transactions.
Locks protect read-modify-write sequences from other Guara clients. The default wait is five
seconds; Python `OpenTruth(..., lock_timeout=...)` and `restore_backup(..., lock_timeout=...)` accept
0–60 seconds. A timeout produces `WorkspaceBusy` in Python and `WORKSPACE_BUSY` in CLI/MCP responses.
Retry once the other operation has finished; do not delete lock files to bypass the lock.

The OS releases the advisory lock on process exit/crash. Small `.opentruth-lock-*` marker files
remain outside the data directory and are ignored by Git; their presence alone does not mean a
workspace is busy. Lock files contain no credentials or evidence. Single trusted OS user only:
uncooperative writers, direct SQL edits, untrusted source mutations, network filesystem locking,
and distributed/multi-user service operation are not guaranteed. Slow operations can block other
clients. SQLite retains its own five-second busy timeout for external connections.

## Reproducible observation

Run `python scripts/benchmark.py --claims 5000` from the checkout. It creates a temporary synthetic
store, reopens it, fetches a page, checks conflicts among matching candidates, and reports timings.
One local Python 3.12.14/Linux run measured: 5,000 inserts in 0.941 s, reopening in 0.00074 s,
a 25-record filtered page in 0.00151 s, and 49 comparisons in 0.00149 s. This is a single warm local
observation, not a cross-version speedup measurement or performance guarantee. CI tests verify
pagination, index selection, omitted histories, persistence and batch correctness without timing
thresholds.

CLI clients may set `--lock-timeout 0.5` before the command to bound their wait explicitly.
