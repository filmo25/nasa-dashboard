PRAGMA foreign_keys = ON;

-- ============================================================
-- STATUS
-- ============================================================

CREATE TABLE IF NOT EXISTS status (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- TECHNOLOGIES
-- Flat list of the 17 technology categories
-- ============================================================

CREATE TABLE IF NOT EXISTS technologies (
    id INTEGER PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- STATES
-- ============================================================

CREATE TABLE IF NOT EXISTS states (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- DESTINATIONS
-- ============================================================

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);


-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    start_date TEXT,
    end_date TEXT,
    status_id INTEGER,
    view_count INTEGER NOT NULL DEFAULT 0,
    last_updated TEXT,

    FOREIGN KEY (status_id)
        REFERENCES status(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
);


-- ============================================================
-- PROJECT ↔ TECHNOLOGY
-- Many-to-many relationship
-- ============================================================

CREATE TABLE IF NOT EXISTS pj_tech (
    project_id INTEGER NOT NULL,
    technology_id INTEGER NOT NULL,

    PRIMARY KEY (project_id, technology_id),

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (technology_id)
        REFERENCES technologies(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- PROJECT ↔ STATE
-- Many-to-many relationship
-- ============================================================

CREATE TABLE IF NOT EXISTS pj_states (
    project_id INTEGER NOT NULL,
    state_id INTEGER NOT NULL,

    PRIMARY KEY (project_id, state_id),

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (state_id)
        REFERENCES states(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- PROJECT ↔ DESTINATION
-- Many-to-many relationship
-- ============================================================

CREATE TABLE IF NOT EXISTS pj_dest (
    project_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,

    PRIMARY KEY (project_id, destination_id),

    FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    FOREIGN KEY (destination_id)
        REFERENCES destinations(id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
);


-- ============================================================
-- DATABASE METADATA
-- Singleton table: only one row is allowed
-- ============================================================

CREATE TABLE IF NOT EXISTS database_info (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    creation_date TEXT,
    last_update_date TEXT
);


-- ============================================================
-- IMPORT / UPDATE LOG
-- ============================================================

CREATE TABLE IF NOT EXISTS updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    projects_added INTEGER NOT NULL DEFAULT 0,
    projects_updated INTEGER NOT NULL DEFAULT 0,
    projects_deleted INTEGER NOT NULL DEFAULT 0
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_projects_status
    ON projects(status_id);

CREATE INDEX IF NOT EXISTS idx_projects_start_date
    ON projects(start_date);

CREATE INDEX IF NOT EXISTS idx_projects_end_date
    ON projects(end_date);

CREATE INDEX IF NOT EXISTS idx_projects_last_updated
    ON projects(last_updated);

CREATE INDEX IF NOT EXISTS idx_pj_tech_technology
    ON pj_tech(technology_id);

CREATE INDEX IF NOT EXISTS idx_pj_states_state
    ON pj_states(state_id);

CREATE INDEX IF NOT EXISTS idx_pj_dest_destination
    ON pj_dest(destination_id);