# SPDX-License-Identifier: GPL-3.0-or-later

import copy
from db.storage import DBState, save_db

players = DBState.players
teams = DBState.teams
matches = DBState.matches

previous_state = None


def save():
    global previous_state
    previous_state = (
        copy.deepcopy(players),
        copy.deepcopy(teams),
        copy.deepcopy(matches),
    )
    save_db()


def undo():
    global previous_state
    if previous_state is None:
        print("No operation to undo.")
        return
    players[:], teams[:], matches[:] = copy.deepcopy(previous_state)
    save_db()
    print("Last operation undone.")
