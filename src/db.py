# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of the TrueSkill CLI project.
#
# Copyright (C) 2024 Drew Jensen
#
# TrueSkill CLI is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# TrueSkill CLI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json, os, shutil, sqlite3, sys
from models import Match, Player, Team

DB_PATH = 'league.db'

def set_db_path(path):
  global DB_PATH
  DB_PATH = path

def resource_path(filename):
  base = getattr(sys, '_MEIPASS', os.path.abspath("."))
  return os.path.join(base, filename)

def init_db():
  if not os.path.exists(DB_PATH):
    with open(resource_path('schemas.sql')) as f:
      sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql)
    conn.commit()
    conn.close()

def load_db():
  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()

  c.execute("SELECT id, name, mu, sigma FROM players")
  players = [Player(*row) for row in c.fetchall()]

  c.execute("SELECT id FROM teams")
  teams = [Team(row[0]) for row in c.fetchall()]

  c.execute("SELECT team_id, player_id FROM team_players")
  for team_id, player_id in c.fetchall():
    team = next(t for t in teams if t.id == team_id)
    player = next(p for p in players if p.id == player_id)
    team.players.append(player)

  c.execute("SELECT id, datetime FROM matches")
  matches = [Match(id=row[0], datetime=row[1]) for row in c.fetchall()]

  c.execute("SELECT match_id, team_id, place, score FROM match_teams")
  for match_id, team_id, place, score in c.fetchall():
    match = next(m for m in matches if m.id == match_id)
    team = next(t for t in teams if t.id == team_id)
    match.match_teams.append({'team': team, 'place': place, 'score': score})

  conn.close()
  return players, teams, matches

def save_db(players, teams, matches):
  # Backup first
  if os.path.exists(DB_PATH):
    shutil.copy(DB_PATH, 'league_backup.db')

  conn = sqlite3.connect(DB_PATH)
  c = conn.cursor()

  c.execute("DELETE FROM players")
  for p in players:
    c.execute("INSERT INTO players (id, name, mu, sigma) VALUES (?, ?, ?, ?)",
              (p.id, p.name, p.mu, p.sigma))

  c.execute("DELETE FROM teams")
  for t in teams:
    c.execute("INSERT INTO teams (id) VALUES (?)", (t.id,))

  c.execute("DELETE FROM team_players")
  for t in teams:
    for p in t.players:
      c.execute("INSERT INTO team_players (team_id, player_id) VALUES (?, ?)", (t.id, p.id))

  c.execute("DELETE FROM matches")
  for m in matches:
    c.execute("INSERT INTO matches (id, datetime) VALUES (?, ?)", (m.id, m.datetime))

  c.execute("DELETE FROM match_teams")
  for m in matches:
    for mt in m.match_teams:
      c.execute("INSERT INTO match_teams (match_id, team_id, place, score) VALUES (?, ?, ?, ?)",
                (m.id, mt['team'].id, mt['place'], mt['score']))

  conn.commit()
  conn.close()

def export_db(json_path='league.json'):
  players_data = [{'id': p.id, 'name': p.name, 'mu': p.mu, 'sigma': p.sigma} for p in players]
  teams_data = [{'id': t.id, 'players': [p.id for p in t.players]} for t in teams]
  matches_data = [{
    'id': m.id,
    'datetime': m.datetime,
    'match_teams': [
      {'team_id': mt['team'].id, 'place': mt['place'], 'score': mt['score']}
      for mt in m.match_teams
    ]
  } for m in matches]

  with open(json_path, 'w', encoding='utf-8') as f:
    json.dump({
      'players': players_data,
      'teams': teams_data,
      'matches': matches_data
    }, f, indent=2)

  print(f"Database exported to {json_path}")

def import_db(json_path='league.json'):
  global players, teams, matches

  if not os.path.exists(json_path):
    print(f"Error: {json_path} does not exist.")
    return

  with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

  id_to_player = {}
  players = []
  for p in data['players']:
    player = Player(p['id'], p['name'], p['mu'], p['sigma'])
    id_to_player[p['id']] = player
    players.append(player)

  id_to_team = {}
  teams = []
  for t in data['teams']:
    team_players = [id_to_player[pid] for pid in t['players']]
    team = Team(t['id'], players=team_players)
    id_to_team[t['id']] = team
    teams.append(team)

  matches = []
  for m in data['matches']:
    match_teams = []
    for mt in m['match_teams']:
      match_teams.append({
        'team': id_to_team[mt['team_id']],
        'place': mt['place'],
        'score': mt['score']
      })
    match = Match(m['id'], match_teams, datetime=m['datetime'])
    matches.append(match)

  print(f"Database imported from {json_path}")