/*
 *  Synapse Cteep
 */

CREATE TABLE IF NOT EXISTS solicitations ( id INTEGER PRIMARY KEY, event_id TEXT NOT NULL, status TEXT NOT NULL, UNIQUE (event_id) );
CREATE INDEX IF NOT EXISTS solicitations_event ON solicitations ( event_id );
