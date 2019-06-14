CREATE TABLE IF NOT EXISTS solicitation_event (solicitation_id TEXT, event_id TEXT, PRIMARY KEY(solicitation_id, event_id));

CREATE INDEX IF NOT EXISTS solicitation ON solicitation_event ( solicitation_id );
CREATE INDEX IF NOT EXISTS s_event ON solicitation_event ( event_id );