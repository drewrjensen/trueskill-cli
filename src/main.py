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

import argparse
from cli import run_cli
from db import init_db, set_db_path

VERSION = "v1.0.10"

def main():
  parser = argparse.ArgumentParser(description="TrueSkill League CLI")
  parser.add_argument('--version', action='version', version=f'TrueSkill CLI {VERSION}')
  parser.add_argument('--db-path', default='league.db', help='Path to database file (default: league.db)')
  sub = parser.add_subparsers(dest='cmd')

  # players
  players_parser = sub.add_parser('players', help='Manage players')
  players_parser.add_argument('action', choices=['list', 'add', 'delete'], nargs='?', default='list', help='Action to perform')
  players_parser.add_argument('name', nargs='?', help='Player name(s)')

  # rankings
  sub.add_parser('rankings', help='Show player rankings')

  # matches
  matches_parser = sub.add_parser('matches', help='Manage matches')
  matches_parser.add_argument('action', choices=['add', 'list', 'edit', 'delete'], nargs='?', default='list', help='Action to perform')
  matches_parser.add_argument('arg', nargs='?', help='Argument for action (participants for add, match_id for edit/delete)')
  matches_parser.add_argument('--time', help='Optional ISO datetime (e.g., 2025-04-27T14:30) for matches add')

  # undo
  sub.add_parser('undo', help='Undo last operation')

  args = parser.parse_args()

  set_db_path(args.db_path)

  if args.cmd is None:
    init_db()
    parser.print_help()
  else:
    run_cli(args)

if __name__ == "__main__":
  main()