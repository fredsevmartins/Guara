# Backup, restore, and source byte integrity

These operations are offline. File checksums verify bytes, not scientific reliability, authorship,
or the truth of a claim. Sources retain their independent `verification_status: NOT_EVALUATED`.

## Source integrity

```sh
opentruth source verify
opentruth source verify SOURCE_UUID
opentruth --format text source verify
```

Results distinguish INTACT, ALTERED, MISSING, UNREADABLE_OR_UNSAFE, and NO_LOCAL_FILE. The last
means metadata-only registration, not a successful byte check. The `ok` flag is false for any
altered, missing, or unsafe file; the CLI then exits 1 while still returning the structured report.
No source status or stored hash is changed to conceal mismatches. Restore the bytes from a trusted
backup or register a new source; do not overwrite its original hash to make a check pass.

## Complete backup

From the allowed workspace, with an existing output parent directory:

```sh
opentruth backup snapshot.zip
# Equivalent legacy JSON input:
opentruth backup --json '{"archive_path":"snapshot.zip"}'
```

Backup format 1 is a ZIP containing `manifest.json`, a consistent SQLite snapshot obtained through
SQLite's backup API, and the exact registered local source copies under `files/UUID`. The manifest
records SHA-256 and byte size for every database/source member. Metadata-only sources have no file
member. Backup aborts if a referenced source is missing, altered, unsafe, or oversized. Existing
archives are never overwritten. Archive paths must be workspace-relative and outside the live data
directory, with no traversal, symlinks, or junctions. Unreferenced orphan copies are not included.

## Restore without overwriting live data

```sh
opentruth restore snapshot.zip --data-dir restored-evidence
```

Restore does not open or initialize the current live database. It checks member names, duplicates,
size limits, checksums, schema version, SQLite integrity, foreign keys, record JSON, and agreement
between database source hashes and stored bytes. It stages the contents privately and publishes the
verified directory only after validation. It never extracts arbitrary archive paths. The destination
must not exist, including as a symlink; existing databases are never merged or replaced.

Open the restored store using Python:

```python
from opentruth import OpenTruth
from opentruth.backup import restore_backup

restore_backup(".", "snapshot.zip", data_dir="restored-evidence")
app = OpenTruth(".", data_dir="restored-evidence")
print(app.verify_sources())
app.close()
```

For restoration into the default `.opentruth`, use a **new workspace** with no initialized data
folder, copy the archive there, and run `opentruth --workspace NEW_WORKSPACE restore snapshot.zip`.
Keep the original workspace intact until you have checked the restored records and files.

## Boundaries

Format 1 supports a database up to 256 MiB, source files up to 20 MiB each, at most 10,000 source
files, an 8 MiB manifest, and a total database/source size up to 1 GiB. Limits are checked during
creation and restoration. Checksums detect byte changes; an attacker can rewrite a manifest, so
they do not authenticate archives. Restore only trusted backups. ZIP is not encrypted: protect
archives as carefully as the evidence itself. Interrupted backup creation may leave a partial
output; an interrupted restore can leave a staging directory. Verify rather than trust filenames.

Do not mutate source/storage directories, restore, or run multiple restores concurrently. This is
a single-user trusted-workspace workflow. SQLite snapshot consistency does not make external source
files transactional. No JSON-export import, schema downgrade, or database repair is implemented.
