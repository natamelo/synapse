/*
 *  Synapse Cteep
 */

CREATE TABLE IF NOT EXISTS solicitations ( id INTEGER PRIMARY KEY, sender_user_id TEXT,event_id TEXT,
                                           status TEXT NOT NULL, action TEXT, substation_code TEXT,
                                           equipment_type TEXT, equipment_code TEXT);
CREATE INDEX IF NOT EXISTS solicitations_event ON solicitations ( event_id );
