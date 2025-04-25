import argparse
import ast
from collections import defaultdict
from datetime import datetime
from db import init_db, load_db, save_db
from models import Match, Player, Team, recalculate_ratings_from
from ratings import update_ratings
import re
import sys
from trueskill import Rating

players, teams, matches = [], [], []

def load():
  global players, teams, matches
  players, teams, matches = load_db()

def save():
  save_db(players, teams, matches)

def list_players():
  for p in sorted(players, key=lambda p: p.name):
    print(f"{p.name} — μ={p.mu:.2f}, σ={p.sigma:.2f}")

def add_player(name):
  if any(p.name == name for p in players):
    print("Player already exists.")
  new_id = max((p.id for p in players), default=0) + 1
  players.append(Player(new_id, name, mu=25.0, sigma=8.333))
  save()
  print(f"Player '{name}' added.")

def delete_player(name):
  global players
  players = [p for p in players if p.name != name]
  save()
  print(f"Deleted player '{name}'.")

def show_rankings():
  for p in sorted(players, key=lambda p: -p.mu):
    print(f"{p.name}: μ={p.mu:.2f}, σ={p.sigma:.2f}")

def add_match(input_str):
  try:
    parsed = parse_participants(input_str)
    resolved = []
    for team in parsed:
      players_in_team = [next(p for p in players if p.name == name) for name in team]
      resolved.append(players_in_team)

    # Update ratings
    update_ratings(*resolved)

    # Record match
    match_id = max((m.id for m in matches), default=0) + 1
    match = Match(id=match_id)
    for place, team_players in enumerate(resolved, start=1):
      team_id = max((t.id for t in teams), default=0) + 1
      team = Team(id=team_id, players=team_players)
      teams.append(team)
      match.match_teams.append({'team': team, 'place': place, 'score': None})
    match.played_at = datetime.now().isoformat(timespec='minutes')
    matches.append(match)

    save()
    print(f"Match recorded at {match.played_at}")
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
          print(f"      {match.datetime} → {' > '.join(team_descriptions)}")

def edit_match(datetime_str):
  try:
    match = next(m for m in matches if m.datetime.startswith(datetime_str))
  except StopIteration:
    print(f"No match found with timestamp {datetime_str}")
    return

  print(f"Editing match from {match.datetime}")
  for i, entry in enumerate(match.match_teams, start=1):
    names = ", ".join(p.name for p in entry['team'].players)
    print(f"  {i}. {names}")

  new_input = input("Enter new participants (comma-separated, use brackets for teams): ")
  try:
    entries = ast.literal_eval(f"[{new_input}]")
    resolved = []
    for entry in entries:
      if isinstance(entry, list):
        team = [next(p for p in players if p.name == name) for name in entry]
      else:
        team = [next(p for p in players if p.name == entry)]
      resolved.append(team)

    # Replace teams and match teams
    new_match_teams = []
    for place, team_players in enumerate(resolved, start=1):
      team_id = max((t.id for t in teams), default=0) + 1
      team = Team(id=team_id, players=team_players)
      teams.append(team)
      new_match_teams.append({'team': team, 'place': place, 'score': None})
    match.match_teams = new_match_teams

    recalculate_ratings_from(match.datetime, players, matches)
    save()
    print("Match updated.")

    # Reset all player ratings
    for player in players:
      player.trueskill = Rating()

    # Re-apply every match in order
    for match in sorted(matches, key=lambda m: m.datetime):
      recalculate_ratings_from(match.datetime, players, matches)
  except Exception as e:
    print(f"Failed to edit match: {e}")

def parse_participants(input_str):
  """
  Parse input like 'Ham,bobthecop11,[SabbaticGoat,gingikinz]'
  into [['Ham'], ['bobthecop11'], ['SabbaticGoat', 'gingikinz']]
  """
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

def main():
  init_db()
  load()
  parser = argparse.ArgumentParser(description="TrueSkill League CLI")
  sub = parser.add_subparsers(dest='cmd')

  # players
  p = sub.add_parser('players')
  p.add_argument('action', choices=['list', 'add', 'delete'], nargs='?', default='list')
  p.add_argument('name', nargs='?')

  # rankings
  sub.add_parser('rankings')

  # matches
  m = sub.add_parser('matches')
  m.add_argument('action', choices=['add', 'list', 'edit'], nargs='?', default='list')
  m.add_argument('arg', nargs='?')

  args = parser.parse_args()

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
      add_match(args.arg)
    elif args.action == 'list':
      list_matches()
    elif args.action == 'edit' and args.arg:
      edit_match(args.arg)

  else:
    parser.print_help()

if __name__ == '__main__':
  main()