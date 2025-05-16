# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import sqlite3
import sys
from models import Player, Team, Match

DB_PATH = "league.db"


class DBState:
    players = []
    teams = []
    matches = []


def set_db_path(path):
    global DB_PATH
    DB_PATH = path


def resource_path(filename):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, filename)


def init_db():
    if not os.path.exists(DB_PATH):
        with open(resource_path("schemas.sql")) as f:
            sql = f.read()
        conn = sqlite3.connect(DB_PATH)
        conn.executescript(sql)
        conn.commit()
        conn.close()


def load_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    DBState.players.clear()
    c.execute("SELECT id, name, mu, sigma FROM players")
    DBState.players.extend(Player(*row) for row in c.fetchall())

    DBState.teams.clear()
    c.execute("SELECT id FROM teams")
    DBState.teams.extend(Team(row[0]) for row in c.fetchall())

    c.execute("SELECT team_id, player_id FROM team_players")
    for team_id, player_id in c.fetchall():
        team = next(t for t in DBState.teams if t.id == team_id)
        player = next(p for p in DBState.players if p.id == player_id)
        team.players.append(player)

    DBState.matches.clear()
    c.execute("SELECT id, datetime FROM matches")
    DBState.matches.extend(Match(id=row[0], datetime=row[1]) for row in c.fetchall())

    c.execute("SELECT match_id, team_id, place, score FROM match_teams")
    for match_id, team_id, place, score in c.fetchall():
        match = next(m for m in DBState.matches if m.id == match_id)
        team = next(t for t in DBState.teams if t.id == team_id)
        match.match_teams.append({"team": team, "place": place, "score": score})

    conn.close()


def save_db():
    if os.path.exists(DB_PATH):
        shutil.copy(DB_PATH, "league_backup.db")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("DELETE FROM players")
    for p in DBState.players:
        c.execute(
            "INSERT INTO players (id, name, mu, sigma) VALUES (?, ?, ?, ?)",
            (p.id, p.name, p.mu, p.sigma),
        )

    c.execute("DELETE FROM teams")
    for t in DBState.teams:
        c.execute("INSERT INTO teams (id) VALUES (?)", (t.id,))

    c.execute("DELETE FROM team_players")
    for t in DBState.teams:
        for p in t.players:
            c.execute(
                "INSERT INTO team_players (team_id, player_id) VALUES (?, ?)",
                (t.id, p.id),
            )

    c.execute("DELETE FROM matches")
    for m in DBState.matches:
        c.execute(
            "INSERT INTO matches (id, datetime) VALUES (?, ?)", (m.id, m.datetime)
        )

    c.execute("DELETE FROM match_teams")
    for m in DBState.matches:
        for mt in m.match_teams:
            c.execute(
                "INSERT INTO match_teams (match_id, team_id, place, score) VALUES (?, ?, ?, ?)",
                (m.id, mt["team"].id, mt["place"], mt["score"]),
            )

    conn.commit()
    conn.close()