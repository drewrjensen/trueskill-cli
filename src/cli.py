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

import ast, copy
from collections import defaultdict
from datetime import datetime
from db import init_db, load_db, save_db, export_db, import_db
from models import Match, Player, Team
from ratings import update_ratings, recalculate_ratings_from
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rapidfuzz import process

players, teams, matches = [], [], []
previous_state = None  # Snapshot for undo

def load():
  global players, teams, matches
  players, teams, matches = load_db()

def save():
  global previous_state
  previous_state = (
    copy.deepcopy(players),
    copy.deepcopy(teams),
    copy.deepcopy(matches),
  )
  save_db(players, teams, matches)

# ----------------
# Helpers
# ----------------

def find_player(name):
  """Find a player by name (case insensitive), or fuzzy suggest."""
  lowered = name.lower()
  for p in players:
    if p.name.lower() == lowered:
      return p

  # Fuzzy match if exact match not found
  player_names = [p.name for p in players]
  matches = process.extract(name, player_names, limit=1, score_cutoff=80)
  if matches:
    suggestion, score, _ = matches[0]
    print(f"No exact match for '{name}'. Did you mean '{suggestion}'?")
    return next(p for p in players if p.name == suggestion)

  return None

def parse_participants(input_str):
  participants = []
  buffer = ""
  inside_team = False
  for char in input_str:
    if char == '[':
      inside_team = True
      buffer = ""
    elif char == ']':
      inside_team = False
      team = [name.strip() for name in buffer.split(',') if name.strip()]
      participants.append(team)
      buffer = ""
    elif char == ',' and not inside_team:
      if buffer.strip():
        participants.append([buffer.strip()])
      buffer = ""
    else:
      buffer += char
  if buffer.strip():
    participants.append([buffer.strip()])
  return participants

# ----------------
# CLI COMMANDS
# ----------------

def add_player(names):
  for name in names.split(','):
    name = name.strip()
    if not name:
      continue
    if any(p.name.lower() == name.lower() for p in players):
      print(f"Player '{name}' already exists.")
    else:
      new_id = max((p.id for p in players), default=0) + 1
      players.append(Player(new_id, name, mu=25.0, sigma=8.333))
      print(f"Player '{name}' added.")
  save()

def list_players():
  sorted_players = sorted(players, key=lambda p: -p.mu)
  if not sorted_players:
    print("No players found.")
    return

  num_players = len(sorted_players)
  pad_width = len(str(num_players))
  longest_name = max(len(p.name) for p in sorted_players)

  for idx, p in enumerate(sorted_players, start=1):
    rank_str = f"({str(idx).rjust(pad_width)})"
    name_str = p.name.ljust(longest_name)
    print(f"{rank_str} {name_str} - μ={p.mu:.2f}, σ={p.sigma:.2f}")

def delete_player(name):
  global players
  players = [p for p in players if p.name.lower() != name.lower()]
  save()
  print(f"Deleted player '{name}'.")

def show_rankings():
  for p in sorted(players, key=lambda p: -p.mu):
    print(f"{p.name}: μ={p.mu:.2f}, σ={p.sigma:.2f}")

def add_match(input_str, datetime_override=None):
  try:
    parsed = parse_participants(input_str)
    resolved = []
    for team in parsed:
      players_in_team = []
      for name in team:
        player = find_player(name)
        if not player:
          raise ValueError(f"Player '{name}' does not exist.")
        players_in_team.append(player)
      resolved.append(players_in_team)

    update_ratings(*resolved)

    match_id = max((m.id for m in matches), default=0) + 1
    match = Match(id=match_id)

    for place, team_players in enumerate(resolved, start=1):
      team_id = max((t.id for t in teams), default=0) + 1
      team = Team(id=team_id, players=team_players)
      teams.append(team)
      match.match_teams.append({'team': team, 'place': place, 'score': None})

    if datetime_override:
      try:
        datetime.fromisoformat(datetime_override)
        match.datetime = datetime_override
      except ValueError:
        print("Invalid datetime format. Using current time instead.")
        match.datetime = datetime.now().isoformat(timespec='minutes')
    else:
      match.datetime = datetime.now().isoformat(timespec='minutes')

    matches.append(match)
    save()
    print(f"Match recorded at {match.datetime}")
  except Exception as e:
    print(f"Error adding match: {e}")

def list_matches():
  if not matches:
    print("No matches recorded.")
    return

  grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

  for match in matches:
    dt = datetime.fromisoformat(match.datetime)
    grouped[dt.year][dt.month][dt.day].append(match)

  for year in sorted(grouped):
    print(f"{year}:")
    for month in sorted(grouped[year]):
      print(f"  {month:02}:")
      for day in sorted(grouped[year][month]):
        print(f"    {day:02}:")
        for match in grouped[year][month][day]:
          team_descriptions = []
          for entry in match.match_teams:
            names = ", ".join(p.name for p in entry['team'].players)
            team_descriptions.append(f"[{names}]")
          time_only = datetime.fromisoformat(match.datetime).strftime("%H:%M")
          print(f"      {time_only} : {match.id} -> {' > '.join(team_descriptions)}")

def edit_match(match_id_str):
  try:
    match_id = int(match_id_str)
    match = next(m for m in matches if m.id == match_id)
  except (ValueError, StopIteration):
    print(f"No match found with ID {match_id_str}")
    return

  print(f"Editing match {match.id} ({match.datetime})")
  for i, entry in enumerate(match.match_teams, start=1):
    names = ", ".join(p.name for p in entry['team'].players)
    print(f"  {i}. {names}")

  player_names = [p.name for p in players]
  player_completer = WordCompleter(player_names, ignore_case=True)

  new_input = prompt(
    "Enter new participants (comma-separated, use brackets for teams) or leave blank to keep: ",
    completer=player_completer
  )
  if new_input.strip():
    try:
      entries = ast.literal_eval(f"[{new_input}]")
      resolved = []
      for entry in entries:
        if isinstance(entry, list):
          team = [find_player(name) for name in entry]
        else:
          team = [find_player(entry)]
        if None in team:
          raise ValueError("One or more player names not found.")
        resolved.append(team)

      old_structure = [
        sorted(p.name for p in entry['team'].players)
        for entry in match.match_teams
      ]
      new_structure = [
        sorted(p.name for p in team_players)
        for team_players in resolved
      ]

      if old_structure != new_structure:
        new_match_teams = []
        for place, team_players in enumerate(resolved, start=1):
          team_id = max((t.id for t in teams), default=0) + 1
          team = Team(id=team_id, players=team_players)
          teams.append(team)
          new_match_teams.append({'team': team, 'place': place, 'score': None})
        match.match_teams = new_match_teams

    except Exception as e:
      print(f"Failed to edit teams: {e}")
      return

  new_dt = input(f"Enter new datetime (YYYY-MM-DDTHH:MM) [default: {match.datetime}]: ").strip()
  if new_dt:
    try:
      datetime.fromisoformat(new_dt)
      match.datetime = new_dt
    except ValueError:
      print("Invalid datetime format. Keeping existing time.")

  recalculate_ratings_from(match.datetime, players, matches)
  save()
  print("Match updated.")

def delete_match(match_id_str):
  try:
    match_id = int(match_id_str)
    match = next(m for m in matches if m.id == match_id)
    matches.remove(match)
    recalculate_ratings_from(match.datetime, players, matches)
    save()
    print(f"Match {match_id} deleted.")
  except (ValueError, StopIteration):
    print(f"No match found with ID {match_id_str}")

def undo():
  global players, teams, matches, previous_state
  if previous_state is None:
    print("No operation to undo.")
    return
  players, teams, matches = copy.deepcopy(previous_state)
  save_db(players, teams, matches)
  print("Last operation undone.")

def run_cli(args):
  init_db()
  load()

  if args.cmd == 'players':
    if args.action == 'list':
      list_players()
    elif args.action == 'add' and args.name:
      add_player(args.name)
    elif args.action == 'delete' and args.name:
      delete_player(args.name)

  elif args.cmd == 'rankings':
    show_rankings()

  elif args.cmd == 'matches':
    if args.action == 'add' and args.arg:
      add_match(args.arg, args.time)
    elif args.action == 'list':
      list_matches()
    elif args.action == 'edit' and args.arg:
      edit_match(args.arg)
    elif args.action == 'delete' and args.arg:
      delete_match(args.arg)

  elif args.cmd == 'undo':
    undo()

  elif args.cmd == 'export':
    json_path = args.db_path.rsplit('.', 1)[0] + '.json'
    export_db(json_path)

  elif args.cmd == 'import':
    json_path = args.db_path.rsplit('.', 1)[0] + '.json'
    import_db(json_path)
    save()