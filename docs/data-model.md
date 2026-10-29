# Data model and migrations

Schema version 1 uses UUID entity keys and JSON payloads in relational tables:

| Table | Purpose |
|---|---|
| claims | Current statement and structured fields |
| sources | Registered metadata, checksum and portable file reference |
| evidence_links | Claim/source foreign keys and attributed relationships |
| claim_revisions | Ordered full claim snapshots, including initial wording |
| review_events | Ordered append-only API audit events |
| conflict_records | Timestamped comparison results with tolerances |
| claim_search | Optional derived FTS5 index |

Foreign keys are enabled per connection. Evidence endpoints and audit lookup columns are indexed.
Creation and revision operations update snapshots and events in one transaction. Stored file copies
are removed if registration fails. An interrupted process can leave an orphan copy: back up and
inspect before manual cleanup. API history is append-only, but SQLite is not tamper-proof.

`PRAGMA user_version` is the migration marker. Version 0 initializes missing tables without dropping
existing data; version 1 is reused; newer versions are rejected. Back up before upgrades. There is
no JSON import or automated repair command. Complete archive restoration is available separately. Keep database and files together for a complete backup.

The v0.1 hardening update adds optional JSON fields without changing table layout or schema
version: evidence `claim_revision` and comparison `inputs`. Existing records are not rewritten.
Missing link revisions are interpreted conservatively as revision 1; historical comparisons
without `inputs` retain their original limitations. See the evidence and comparison guides.

The v0.1.1 optional claim `context_template` field and derived comparison explanations do not
change the schema version. Legacy claim payloads remain readable and revisable.
