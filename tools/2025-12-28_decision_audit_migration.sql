-- Migration: Add revoked column to match_decisions and create decision_audit table

ALTER TABLE match_decisions
ADD COLUMN revoked BOOLEAN NOT NULL DEFAULT FALSE;

CREATE TABLE IF NOT EXISTS decision_audit (
    id SERIAL PRIMARY KEY,
    decision_id INTEGER NOT NULL REFERENCES match_decisions(id) ON DELETE CASCADE,
    action VARCHAR(32) NOT NULL,
    old_value VARCHAR(64),
    new_value VARCHAR(64),
    user_id VARCHAR(64) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
);
