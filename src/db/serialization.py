# SPDX-License-Identifier: GPL-3.0-or-later

import os
import json
import sqlite3
from db.storage import DB_PATH, DBState
from models import Player, Team, Match
from db.player_days import regenerate_all_player_days

players = DBState.players
teams = DBState.teams
matches = DBState.matches


def export_db(json_path="league.json"):
    players_data = [
        {"id": p.id, "name": p.name, "mu": p.mu, "sigma": p.sigma} for p in players
    ]
    teams_data = [{"id": t.id, "players": [p.id for p in t.players]} for t in teams]
    matches_data = [
        {
            "id": m.id,
            "datetime": m.datetime,
            "match_teams": [
                {"team_id": mt["team"].id, "place": mt["place"], "score": mt["score"]}
                for mt in m.match_teams
            ],
        }
        for m in matches
    ]

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT player_id, date, mu, sigma FROM player_days")
    player_days_data = [
        {"player_id": pid, "date": date, "mu": mu, "sigma": sigma}
        for pid, date, mu, sigma in c.fetchall()
    ]
    conn.close()

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "players": players_data,
                "teams": teams_data,
                "matches": matches_data,
                "player_days": player_days_data,
            },
            f,
            indent=2,
        )

    print(f"Database exported to {json_path}")


def import_db(json_path="league.json"):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist.")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    id_to_player = {}
    players.clear()
    for p in data["players"]:
        player = Player(p["id"], p["name"], p["mu"], p["sigma"])
        id_to_player[p["id"]] = player
        players.append(player)

    id_to_team = {}
    teams.clear()
    for t in data["teams"]:
        team_players = [id_to_player[pid] for pid in t["players"]]
        team = Team(t["id"], players=team_players)
        id_to_team[t["id"]] = team
        teams.append(team)

    matches.clear()
    for m in data["matches"]:
        match_teams = []
        for mt in m["match_teams"]:
            match_teams.append(
                {
                    "team": id_to_team[mt["team_id"]],
                    "place": mt["place"],
                    "score": mt["score"],
                }
            )
        match = Match(m["id"], match_teams, datetime=m["datetime"])
        matches.append(match)

    regenerate_all_player_days()
    print(f"Database imported from {json_path}")
