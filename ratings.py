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

from trueskill import rate, rate_1vs1

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