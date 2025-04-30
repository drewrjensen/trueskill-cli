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

from trueskill import rate, rate_1vs1, Rating

def update_ratings(*args, ranks=None):
  teams = [[p] if not isinstance(p, list) else p for p in args]

  if len(teams) == 2 and all(len(t) == 1 for t in teams):
    p1, p2 = teams[0][0], teams[1][0]
    p1.trueskill, p2.trueskill = rate_1vs1(p1.trueskill, p2.trueskill)
  else:
    rating_groups = [[p.trueskill for p in team] for team in teams]
    input_ranks = ranks if ranks else list(range(len(teams)))
    updated_groups = rate(rating_groups, ranks=input_ranks)
    for new_ratings, team in zip(updated_groups, teams):
      for new_rating, player in zip(new_ratings, team):
        player.trueskill = new_rating

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