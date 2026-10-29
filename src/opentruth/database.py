"""Versioned SQLite schema; all entity payloads are portable JSON."""

import sqlite3

SCHEMA_VERSION = 2
SCHEMA = """
CREATE TABLE IF NOT EXISTS claims(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS sources(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence_links(
 id TEXT PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id),
 source_id TEXT NOT NULL REFERENCES sources(id), payload TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS evidence_claim ON evidence_links(claim_id);
CREATE INDEX IF NOT EXISTS evidence_source ON evidence_links(source_id);
CREATE TABLE IF NOT EXISTS claim_revisions(
 sequence INTEGER PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id), payload TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS revisions_claim ON claim_revisions(claim_id);
CREATE TABLE IF NOT EXISTS review_events(
 sequence INTEGER PRIMARY KEY, entity_id TEXT NOT NULL, payload TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS events_entity ON review_events(entity_id);
CREATE TABLE IF NOT EXISTS conflict_records(
 id TEXT PRIMARY KEY, claim_id TEXT NOT NULL REFERENCES claims(id), payload TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS conflicts_claim ON conflict_records(claim_id);
"""


def connect(path):
    db = sqlite3.connect(path, timeout=5, check_same_thread=False)
    db.execute("PRAGMA foreign_keys=ON")
    try:
        version = db.execute("PRAGMA user_version").fetchone()[0]
        if version > SCHEMA_VERSION:
            raise ValueError("Database schema is newer than this application")
        # DDL, indexes and marker commit together; failed migrations leave the old schema intact.
        db.executescript(
            "BEGIN IMMEDIATE;\n"
            + SCHEMA
            + """
CREATE INDEX IF NOT EXISTS claims_subject_predicate
 ON claims(json_extract(payload, '$.subject'), json_extract(payload, '$.predicate'));
CREATE INDEX IF NOT EXISTS claims_review ON claims(json_extract(payload, '$.review_status'));
PRAGMA user_version=2;
COMMIT;
"""
        )
        return db
    except BaseException:
        db.close()
        raise


def initialize_search(db):
    try:
        initialized = db.execute(
            "SELECT 1 FROM sqlite_master WHERE type='trigger' AND name='opentruth_fts_insert'"
        ).fetchone()
        if initialized:
            # An existing synchronized index needs no full-record scan at startup.
            db.execute("SELECT id FROM claim_search LIMIT 0")
            return True
        db.executescript("""
BEGIN IMMEDIATE;
CREATE VIRTUAL TABLE IF NOT EXISTS claim_search USING fts5(id UNINDEXED, statement);
DELETE FROM claim_search;
INSERT INTO claim_search SELECT id,json_extract(payload,'$.original_statement') FROM claims;
CREATE TRIGGER opentruth_fts_insert AFTER INSERT ON claims BEGIN
 INSERT INTO claim_search VALUES (new.id,json_extract(new.payload,'$.original_statement'));
END;
CREATE TRIGGER opentruth_fts_update AFTER UPDATE ON claims BEGIN
 UPDATE claim_search SET statement=json_extract(new.payload,'$.original_statement') WHERE id=old.id;
END;
CREATE TRIGGER opentruth_fts_delete AFTER DELETE ON claims BEGIN
 DELETE FROM claim_search WHERE id=old.id;
END;
COMMIT;
""")
        return True
    except sqlite3.OperationalError as error:
        db.rollback()
        if "no such module" not in str(error):
            raise
        db.executescript("""
DROP TRIGGER IF EXISTS opentruth_fts_insert;
DROP TRIGGER IF EXISTS opentruth_fts_update;
DROP TRIGGER IF EXISTS opentruth_fts_delete;
""")
        return False
