from datetime import datetime as dt
from ratings import update_ratings
from trueskill import Rating

class Player:
  def __init__(self, id, name, mu, sigma):
    self.id = id
    self.name = name
    self.trueskill = Rating(mu, sigma)

  @property
  def mu(self): return self.trueskill.mu
  @property
  def sigma(self): return self.trueskill.sigma

class Team:
  def __init__(self, id, players=None):
    self.id = id
    self.players = players or []

class Match:
  def __init__(self, id, match_teams=None, datetime=dt.now().isoformat(timespec='minutes')):
    self.id = id
    self.datetime = datetime or dt.now().isoformat(timespec='minutes')
    self.match_teams = match_teams or []

  def apply_results(self):
    teams = [entry['team'].players for entry in self.match_teams]
    ranks = [entry['place'] for entry in self.match_teams] if len(teams) > 2 else None
    update_ratings(*teams) if ranks is None else update_ratings(*teams, ranks=ranks)

def recalculate_all_ratings(players, matches):
  # Reset all player ratings to default
  for player in players:
    player.trueskill = Rating()  # default mu=25.0, sigma=8.333...

  # Reapply all match results in chronological order
  matches_sorted = sorted(matches, key=lambda m: m.played_at)
  for match in matches_sorted:
    match.apply_results()

def recalculate_ratings_from(match_point, players, matches):
  # Step 1: Collect matches at or after match_point
  matches_to_recalc = [m for m in matches if m.datetime >= match_point]

  # Step 2: Identify affected player ids
  affected_player_ids = set()
  for match in matches_to_recalc:
    for entry in match.match_teams:
      for player in entry['team'].players:
        affected_player_ids.add(player.id)

  # Step 3: Reset affected players only
  for player in players:
    if player.id in affected_player_ids:
      player.trueskill = Rating()

  # Step 4: Reapply results for affected matches only
  for match in sorted(matches_to_recalc, key=lambda m: m.datetime):
    match.apply_results()