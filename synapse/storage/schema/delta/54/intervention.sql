/*
 *  Synapse Cteep
 */

CREATE TABLE IF NOT EXISTS interventions ( id INTEGER PRIMARY KEY, event_id TEXT, status TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS interventions_event ON interventions ( event_id );
