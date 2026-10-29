"""Versioned SQLite schema; all entity payloads are portable JSON."""

import sqlite3

SCHEMA_VERSION = 1
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
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    version = db.execute("PRAGMA user_version").fetchone()[0]
    if version > SCHEMA_VERSION:
        db.close()
        raise ValueError("Database schema is newer than this application")
    with db:
        db.executescript(SCHEMA)
        db.execute("PRAGMA user_version=1")
    return db
