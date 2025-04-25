import os, shutil, sqlite3, sys
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