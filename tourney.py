import elo
import glicko2, trueskill
import os, sqlite3

class Player:
  def __init__(self, id, name, elo=0, glicko=0, trueskill=0):
    self.id = id
    self.name = name
    self.elo = elo
    self.glicko = glicko
    self.trueskill = trueskill

  def update(self, outcome):
    # Update the player's rating based on the outcome of a match
    self.elo = elo.update_elo(self.elo, outcome)
    self.glicko = glicko2.update_glicko(self.glicko, outcome)
    self.trueskill = trueskill.update_trueskill(self.trueskill, outcome)
  
class Team:
  def __init__(self, id, players=[]):
    self.id = id
    self.players = players

class Match:
  def __init__(self, id, match_teams=[]):
    self.id = id
    self.match_teams = match_teams
    # match_team: [
    #   team: Team,
    #   score: int,
    #   place: int
    # ]

def init_db():
  if not os.path.exists('league.db'):
    conn = sqlite3.connect('league.db')
    c = conn.cursor()
    with open('setup_dbs.sql', 'r') as f:
      sql_script = f.read()
    c.executescript(sql_script)
    conn.commit()
    conn.close()

def load_db():
  conn = sqlite3.connect('league.db')
  c = conn.cursor()
  
  # Load players
  c.execute("SELECT id, name, elo, glicko, trueskill FROM players")
  players = [Player(id=row[0], name=row[1], elo=row[2], glicko=row[3], trueskill=row[4]) for row in c.fetchall()]
  
  # Load teams
  c.execute("SELECT id FROM teams")
  teams = [Team(id=row[0]) for row in c.fetchall()]
  
  # Load team players
  c.execute("SELECT team_id, player_id FROM team_players")
  team_players = c.fetchall()
  for team_id, player_id in team_players:
    team = next(t for t in teams if t.id == team_id)
    player = next(p for p in players if p.id == player_id)
    team.players.append(player)
  
  # Load matches
  c.execute("SELECT id FROM matches")
  matches = [Match(id=row[0]) for row in c.fetchall()]
  
  # Load match teams
  c.execute("SELECT match_id, team_id, place, score FROM match_teams")
  match_teams = c.fetchall()
  for match_id, team_id, place, score in match_teams:
    match = next(m for m in matches if m.id == match_id)
    team = next(t for t in teams if t.id == team_id)
    match.match_teams.append({'team': team, 'place': place, 'score': score})
  
  conn.close()
  return players, teams, matches

def save_db(players, teams, matches):
  conn = sqlite3.connect('league.db')
  c = conn.cursor()
  
  # Save players
  c.execute("DELETE FROM players")
  for player in players:
    c.execute("INSERT INTO players (id, name, elo, glicko, trueskill) VALUES (?, ?, ?, ?, ?)",
              (player.id, player.name, player.elo, player.glicko, player.trueskill))
  
  # Save teams
  c.execute("DELETE FROM teams")
  for team in teams:
    c.execute("INSERT INTO teams (id) VALUES (?)", (team.id,))
  
  # Save team players
  c.execute("DELETE FROM team_players")
  for team in teams:
    for player in team.players:
      c.execute("INSERT INTO team_players (team_id, player_id) VALUES (?, ?)", (team.id, player.id))
  
  # Save matches
  c.execute("DELETE FROM matches")
  for match in matches:
    c.execute("INSERT INTO matches (id) VALUES (?)", (match.id,))
  
  # Save match teams
  c.execute("DELETE FROM match_teams")
  for match in matches:
    for match_team in match.match_teams:
      c.execute("INSERT INTO match_teams (match_id, team_id, place, score) VALUES (?, ?, ?, ?)",
                (match.id, match_team['team'].id, match_team['place'], match_team['score']))
  
  conn.commit()
  conn.close()

def main():
  init_db()
  players, teams, matches = load_db()
  
  # Example usage
  for player in players:
    print(f"Player: {player.name}, Elo: {player.elo}, Glicko: {player.glicko}, TrueSkill: {player.trueskill}")
  
  for team in teams:
    print(f"Team ID: {team.id}, Players: {[p.name for p in team.players]}")
  
  for match in matches:
    print(f"Match ID: {match.id}, Teams: {[t['team'].id for t in match.match_teams]}")
  
  # Save changes to the database
  save_db(players, teams, matches)

if __name__ == "__main__": main()