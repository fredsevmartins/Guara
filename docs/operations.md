# Operating a local evidence workspace

Use this runbook with Guara 0.1.3 and one trusted local OS user. All paths below are examples;
substitute an existing workspace you have authorized. See [security](security.md).

## Know where your data lives

| Path relative to workspace | Purpose | Handling |
| --- | --- | --- |
| `.opentruth/evidence.sqlite3` | Current claims, revisions, source metadata, relationships, history, comparisons | Keep with registered source files |
| `.opentruth/files/UUID` | Independent copies of registered local sources | Do not edit or rename |
| `.opentruth-lock-*` | Cooperating-client lock markers | Presence does not mean an operation is active; do not delete to bypass a lock |
| Backup archive path you selected | Database snapshot and registered bytes | Protect and retain independently of the live store |

CLI commands normally open/initialize the default `.opentruth` directory. Python can select another
`data_dir`. The CLI restore `--data-dir` chooses its restore destination; it does not make later CLI
commands use that alternate directory. Inspect an alternate restored directory with Python, or
restore into a new workspace's default directory for normal CLI use.

## Routine checks

```sh
opentruth --version
python -m pip check
opentruth --workspace /absolute/evidence source verify
opentruth --workspace /absolute/evidence --format text claim list --limit 25
```

Inspect integrity entries, not just `ok`: metadata-only sources have `NO_LOCAL_FILE`. In a trusted
multi-process workflow, retry `WORKSPACE_BUSY` after the current operation finishes. Bound the wait
with `--lock-timeout 1` before the command; do not run unbounded retry loops.

## Back up and prove recovery

1. Choose a new archive filename under the workspace and outside `.opentruth`.
2. Run `opentruth --workspace /absolute/evidence backup backup-2026-11-02.zip`.
3. Copy the completed archive to your protected backup destination using your normal file tools.
4. Create a new workspace, copy the archive into it, and restore there without running `init` first.
5. Inspect expected UUIDs, wording, revision history, and source-integrity entries in the restored store.
6. Keep the original store until recovery checks succeed.

The date above is an example, not an automatic naming facility. Existing archive names and restore
directories are not overwritten. A byte-valid backup can still contain incorrect scientific claims.
See [archive limits and restoration](backup-and-integrity.md). Guara does not schedule backups;
choose a cadence and retention period appropriate to your data and rate of change.

## Upgrade and rollback

1. Read the target release notes and [schema compatibility](data-model.md).
2. Stop cooperating CLI/MCP clients and complete a verified backup with the current installation.
3. Use a separate virtual environment for the new version; record `opentruth --version`.
4. Test the new installation on a restored copy before opening the live workspace.
5. Compare expected claims, history, integrity reports, and your required workflows.
6. Switch your client executable paths only after those checks pass.

Opening a schema-1 store upgrades it to schema 2. Application 0.1.3 uses database/export schema 2
and backup format 1. Older applications cannot necessarily open the migrated database. Roll back
with the previous executable and a compatible pre-upgrade backup restored into a new workspace;
do not attempt a manual schema downgrade. Changes made after a backup are not present in it.

## Sharing and retention

For sharing software, use the repository or release downloads. For sharing evidence, review the
content and actor/source metadata before transferring an export or backup. JSON excludes source
bytes; a complete backup includes them. Neither artifact is encrypted or anonymized by Guara.
There is no JSON import, selective redaction, deletion API, or anonymization command in 0.1.3.
Do not promise those functions to collaborators or treat a raw SQL edit as a supported workflow.
Define retention and disposal outside the application according to your requirements.

Uninstalling the Python package does not remove `.opentruth` data or separately copied archives.
Before retiring a workspace, close clients, establish what must be retained, and handle the
workspace, exported files, backups, and original source files through your normal storage process.
Guara does not provide secure erasure or verify disposal of external copies.

## Recovery boundaries

A partial/interrupted backup is not a verified backup. A failed restore can leave a private
staging directory; preserve the original archive and diagnose before cleanup. For corruption,
keep the damaged original and restore a known-good backup elsewhere. Do not delete rows, rewrite
hashes, or remove locks to make an integrity report pass. See [troubleshooting](troubleshooting.md).
