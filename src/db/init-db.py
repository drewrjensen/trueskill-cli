"""Create the SQLite database used to track players and TrueSkill matches."""

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS players (
	id INTEGER PRIMARY KEY,
	name TEXT NOT NULL UNIQUE,
	mu REAL NOT NULL DEFAULT 25.0,
	sigma REAL NOT NULL DEFAULT 8.333333333333334,
	created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS matches (
	id INTEGER PRIMARY KEY,
	played_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS match_players (
	match_id INTEGER NOT NULL,
	player_id INTEGER NOT NULL,
	rank INTEGER NOT NULL,
	mu_before REAL NOT NULL,
	sigma_before REAL NOT NULL,
	mu_after REAL NOT NULL,
	sigma_after REAL NOT NULL,
	PRIMARY KEY (match_id, player_id),
	FOREIGN KEY (match_id) REFERENCES matches(id) ON DELETE CASCADE,
	FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_match_players_player_id
	ON match_players(player_id);
CREATE INDEX IF NOT EXISTS idx_matches_played_at
	ON matches(played_at);
"""


def initialize_database(database_path: str | Path) -> None:
    """Create the database and its tables if they do not already exist."""
    path = Path(database_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as connection:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)
