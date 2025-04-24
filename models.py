from trueskill import Rating
from ratings import update_ratings

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
  def __init__(self, id, match_teams=None):
    self.id = id
    self.match_teams = match_teams or []

  def apply_results(self):
    teams = [entry['team'].players for entry in self.match_teams]
    ranks = [entry['place'] for entry in self.match_teams] if len(teams) > 2 else None
    update_ratings(*teams) if ranks is None else update_ratings(*teams, ranks=ranks)