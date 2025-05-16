# SPDX-License-Identifier: GPL-3.0-or-later

from db.storage import DBState
from models import Player
from cli.util import save


def add_player(names):
    for name in names.split(","):
        name = name.strip()
        if not name:
            continue
        if any(p.name.lower() == name.lower() for p in DBState.players):
            print(f"Player '{name}' already exists.")
        else:
            new_id = max((p.id for p in DBState.players), default=0) + 1
            DBState.players.append(Player(new_id, name, mu=25.0, sigma=8.333))
            print(f"Player '{name}' added.")
    save()


def list_players():
    if not DBState.players:
        print("No players found.")
        return
    sorted_players = sorted(p.name for p in DBState.players)
    print(", ".join(sorted_players))


def delete_player(name):
    name = name.strip().lower()
    index = next((i for i, p in enumerate(DBState.players) if p.name.lower() == name), None)
    if index is not None:
        del DBState.players[index]
        save()
        print(f"Deleted player '{name}'.")
    else:
        print(f"Player '{name}' not found.")
