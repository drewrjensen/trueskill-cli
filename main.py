from db import init_db, load_db, save_db
from models import Match
from ratings import update_ratings

def main():
  init_db()
  players, teams, matches = load_db()

  for match in matches:
    match.apply_results()

  save_db(players, teams, matches)

if __name__ == '__main__': main()