# Troubleshooting

- Import/command not found: activate the installation virtual environment and reinstall editable.
- Unknown record: use the returned UUID and the same `--workspace` used during creation.
- Invalid CLI input: `--json` must contain an object, not a list or malformed JSON; use `--help`.
- File rejected: use a regular relative file under the authorized workspace, without symlinks or `..`.
- FTS5 unavailable: the engine automatically falls back to case-insensitive substring matching.
- Database corrupt: preserve the file, restore a verified backup, and do not delete evidence to
  suppress the error. Newer schema versions are rejected; use a compatible application version.
- MCP unavailable: verify the absolute executable, workspace, installed SDK, and client stdio support.
- Different measurements: inspect registered context, units, and tolerances before interpretation.
- Locked database: finish the other writer; this version targets a trusted single-user workflow.
