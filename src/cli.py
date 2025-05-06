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
from db import players, teams, matches, load_db, save_db, export_db, import_db
from models import Match, Player, Team
from ratings import update_ratings, recalculate_ratings_from
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from rapidfuzz import process

previous_state = None  # Snapshot for undo

def save():
  global previous_state
  previous_state = (
    copy.deepcopy(players),
    copy.deepcopy(teams),
    copy.deepcopy(matches),
  )
  save_db()

# ----------------
# Helpers
# ----------------

def find_player(name):
  lowered = name.lower()
  for p in players:
    if p.name.lower() == lowered:
      return p
  player_names = [p.name for p in players]
  matches_found = process.extract(name, player_names, limit=1, score_cutoff=80)
  if matches_found:
    suggestion, _, _ = matches_found[0]
    print(f"No exact match for '{name}'. Did you mean '{suggestion}'?")
    return next(p for p in players if p.name == suggestion)
  return None

def parse_participants(input_str):
  participants = []
  scores = []
  buffer = ""
  inside_team = False
  tokens = input_str.split()

  i = 0
  while i < len(tokens):
    token = tokens[i]
    if token.startswith('score:'):
      scores = [int(s) for s in token[6:].split(',')]
    else:
      for char in token:
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
        buffer = ""
    i += 1

  return participants, scores

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
  pad_width = len(str(len(sorted_players)))
  longest_name = max(len(p.name) for p in sorted_players)
  for idx, p in enumerate(sorted_players, start=1):
    print(f"({str(idx).rjust(pad_width)}) {p.name.ljust(longest_name)} - μ={p.mu:.2f}, σ={p.sigma:.2f}")

def delete_player(name):
  name = name.strip().lower()
  index = next((i for i, p in enumerate(players) if p.name.lower() == name), None)
  if index is not None:
    del players[index]
    save()
    print(f"Deleted player '{name}'.")
  else:
    print(f"Player '{name}' not found.")

def show_rankings():
  for p in sorted(players, key=lambda p: -p.mu):
    print(f"{p.name}: μ={p.mu:.2f}, σ={p.sigma:.2f}")

def add_match(input_str, datetime_override=None):
  try:
    parsed, scores = parse_participants(input_str)
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
      score = scores[place - 1] if len(scores) >= place else None
      match.match_teams.append({'team': team, 'place': place, 'score': score})

    match.datetime = (
      datetime_override if datetime_override and datetime.fromisoformat(datetime_override)
      else datetime.now().isoformat(timespec='minutes')
    )

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
          team_str = " > ".join(
            f"[{', '.join(p.name for p in mt['team'].players)}]"
            + (f" (score: {mt['score']})" if mt['score'] is not None else "")
            for mt in match.match_teams
          )
          print(f"      {datetime.fromisoformat(match.datetime).strftime('%H:%M')} : {match.id} -> {team_str}")

def undo():
  global previous_state
  if previous_state is None:
    print("No operation to undo.")
    return
  players[:], teams[:], matches[:] = copy.deepcopy(previous_state)
  save_db()
  print("Last operation undone.")

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
    score_str = f" (score: {entry['score']})" if entry['score'] is not None else ""
    print(f"  {i}. {names}{score_str}")

  player_names = [p.name for p in players]
  player_completer = WordCompleter(player_names, ignore_case=True)

  try:
    new_input = prompt(
      "Enter new participants (comma-separated, use brackets for teams, optional 'score:') or leave blank to keep: ",
      completer=player_completer
    )
    if new_input.strip():
      entries, scores = parse_participants(new_input)
      resolved = []
      for entry in entries:
        team = [find_player(name) for name in entry]
        if None in team:
          raise ValueError("One or more player names not found.")
        resolved.append(team)

      if resolved:
        match.match_teams = []
        for place, team_players in enumerate(resolved, start=1):
          team_id = max((t.id for t in teams), default=0) + 1
          team = Team(id=team_id, players=team_players)
          teams.append(team)
          score = scores[place - 1] if len(scores) >= place else None
          match.match_teams.append({'team': team, 'place': place, 'score': score})

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
  except Exception as e:
    print(f"Failed to edit match: {e}")

def run_cli(args):
  load_db()

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

  elif args.cmd == 'undo':
    undo()

  elif args.cmd == 'export':
    json_path = args.db_path.rsplit('.', 1)[0] + '.json'
    export_db(json_path)

  elif args.cmd == 'import':
    json_path = args.db_path.rsplit('.', 1)[0] + '.json'
    print(f"Importing from {json_path}")
    import_db(json_path)
    save()