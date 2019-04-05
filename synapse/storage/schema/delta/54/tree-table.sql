/*
 *  Synapse Cteep
 */

CREATE TABLE IF NOT EXISTS tree_paths (ancestor TEXT NOT NULL, descendant TEXT NOT NULL, path_length BIGINT NOT NULL, PRIMARY KEY(ancestor, descendant), FOREIGN KEY (ancestor) REFERENCES groups(group_id), FOREIGN KEY (descendant) REFERENCES groups(group_id));

