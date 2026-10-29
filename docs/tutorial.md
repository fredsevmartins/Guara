# Executable evidence tutorial

From the source checkout with `.[dev]` installed:

```sh
python -m examples.tutorial
```

The tutorial creates and removes its own temporary workspace. All names, measurements, evidence,
and reviewer strings are synthetic. It works without local source ingestion, including on Windows.
Expected output includes `synthetic: true`, `history_events: 5`, `backup_restored: true`, and
evidence status `CONTRADICTED_BY_REGISTERED_EVIDENCE`. Every transition is assertion-checked, and
CI runs the same tutorial on its configured platforms.

Read [examples/tutorial.py](../examples/tutorial.py) for the complete executable code. The steps:

1. Register a fictional beam claim and an experiment's metadata. Metadata registration alone
   supplies no scientific verification.
2. Record an explicit SUPPORTS relationship with a source location, excerpt, and synthetic actor.
3. Correct the claim's value and wording; inspect INSUFFICIENT_EVIDENCE because earlier evidence
   was assessed against the previous revision.
4. Reassess the relationship as CONTRADICTS with a reason and actor; record NEEDS_REVIEW without
   inventing reviewer attribution.
5. Fetch a lightweight search page and a separate history page.
6. Check integrity. NO_LOCAL_FILE explicitly indicates metadata-only registration, not a checked
   file or independently verified experiment.
7. Create a complete archive, restore into an absent data directory, and verify both the original
   wording and the latest relationship summary survived.

For your own workspace, replace synthetic content and self-attribution with what you actually
observed. See [quickstart](quickstart.md) for CLI syntax and [backup and integrity](backup-and-integrity.md)
for source-file backups, limits, and restoring into a new workspace. Accepted review decisions and
registered evidence remain distinct from independent scientific verification.
