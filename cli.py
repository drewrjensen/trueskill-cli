import argparse
import ast
from datetime import datetime
from db import load_db, save_db
from models import Player, Match, Team
from ratings import update_ratings
import sys

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
    # Parse: "Drew,Emily,[Ridge,Spencer]"
    entries = ast.literal_eval(f"[{input_str}]")
    resolved = []
    for entry in entries:
      if isinstance(entry, list):
        team = [next(p for p in players if p.name == name) for name in entry]
      else:
        team = [next(p for p in players if p.name == entry)]
      resolved.append(team)
    update_ratings(*resolved)
    save()
    print("Match recorded.")
  except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

def main():
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
      print("[match list UI here]")
    elif args.action == 'edit' and args.arg:
      print(f"[edit match at {args.arg}]")

  else:
    parser.print_help()

if __name__ == '__main__':
  main()