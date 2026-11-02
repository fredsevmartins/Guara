# Troubleshooting

Start by recording `opentruth --version`, `python --version`, OS, exact command, and intended
workspace. Use synthetic data in reproductions. See [support](support.md) for where to report it.

## Installation and executable selection

| Symptom | Check | Recovery |
| --- | --- | --- |
| `opentruth` not found | Is the virtual environment active? | Activate it; run `python -m opentruth.cli --version` with that interpreter |
| `ModuleNotFoundError` | Was the wheel installed into this interpreter? | Install the downloaded wheel using `python -m pip install PATH_TO_WHEEL` |
| Dependency conflict | Run `python -m pip check` | Use a fresh virtual environment and reinstall the intended release |
| MCP starts an older version | Inspect the client's absolute executable path | Point it to the verified environment and restart the client |

Do not assume a package exists on PyPI just because a distribution name is known. Install from
[GitHub Releases](https://github.com/fredsevmartins/Guara/releases) or a source checkout.

## CLI failures and output

| Signal | Meaning | Next step |
| --- | --- | --- |
| Exit 2 and usage text | Argument parsing rejected the command | Run that command's `--help`; check flag placement and enum values |
| Exit 1, `INVALID_INPUT_OR_STORAGE` on stderr | Engine input or storage failure | Check UUIDs, required reason/actor fields, JSON objects, workspace, and permissions |
| Exit 1, `WORKSPACE_BUSY` | Another cooperating operation exceeded the wait | Finish the operation, then retry; do not delete lock markers |
| Exit 1 with integrity report on stdout | A file is missing, changed, or unsafe | Inspect each `integrity_status`; preserve discrepancies |
| Garbled redirected text | Consumer decoded UTF-8 using a local code page | Decode subprocess output as UTF-8; update older installations |

Global flags such as `--workspace`, `--format`, and `--lock-timeout` precede the command. Do not
supply one field both in `--json` and a convenience flag. Revisions require nonblank reasons;
acceptance/rejection also requires a reason. Links require nonblank actor, location, and excerpt.
CLI error text intentionally omits raw storage details. Python exceptions can provide local
technical details; sanitize them before reporting.

## Unexpected evidence or search results

- **Unknown UUID or empty store:** check the same `--workspace` was used when creating the record.
  An unintended workspace can initialize a different store. Alternate restored `data_dir` values
  are selected through Python, not a general CLI `--data-dir` flag.
- **Insufficient evidence after correction:** this is expected. Earlier links apply to the old
  revision; explicitly reassess or link new evidence. Review acceptance alone does not add support.
- **Missing search results:** verify filters and spelling; use successive pages after the default
  100 results. FTS5 token matching and the no-FTS substring fallback can differ.
- **No comparison result:** there may be no candidates in that page. Inspect subject, predicate,
  explicit context, unit, and numeric value types. Numeric strings are qualitative.
- **Unexpected potential conflict:** inspect `reason`, `inputs`, normalized units, context, and
  tolerances. Context dictionaries must match exactly; comparisons are recorded snapshots.

See [status interpretation](statuses.md) and [comparison rules](conflict-detection.md).

## Source files, backups, and migrations

- **File rejected:** use a regular workspace-relative file without traversal or symlink components,
  within the 20 MiB limit. Secure local ingestion requires POSIX primitives; metadata workflows
  remain available on Windows.
- **Backup rejected:** choose a new filename with an existing parent, outside the live data
  directory, and verify registered source bytes first. Review archive size/path limits.
- **Restore rejected:** the destination must be absent. Verify the archive checksums and supported
  schema. Preserve the archive; do not alter its manifest to suppress an error.
- **Newer schema or corrupt database:** retain the original, identify the correct application
  version, and restore a known-good compatible backup elsewhere. There is no repair or schema
  downgrade command.

Use the [operations runbook](operations.md) and [backup reference](backup-and-integrity.md).
Do not include private evidence, source excerpts, local usernames, or credentials in public logs.
