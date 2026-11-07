# SPDX-License-Identifier: GPL-3.0-or-later

import copy

import json
from rapidfuzz import process
from db.storage import DBState, save_db


def find_player(name):
    lowered = name.lower()
    for p in DBState.players:
        if p.name.lower() == lowered:
            return p
    player_names = [p.name for p in DBState.players]
    matches_found = process.extract(name, player_names, limit=1, score_cutoff=80)
    if matches_found:
        suggestion, _, _ = matches_found[0]
        print(f"No exact match for '{name}'. Did you mean '{suggestion}'?")
        return next(p for p in DBState.players if p.name == suggestion)
    return None


def parse_match(input_str):
    # String input JSON grammar:
    ## ((Team | Participant)(: Score)?){2,}
    # JSON must be symmetrical, meaning that if one team/participants has a score, the others must have a score as well.

    match = json.loads(input_str)
    if not isinstance(match, list) or len(match) < 2:
        raise ValueError("Match must be a list of at least two teams/participants.")

    return match


previous_state = None


def save():
    global previous_state
    previous_state = (
        copy.deepcopy(DBState.players),
        copy.deepcopy(DBState.teams),
        copy.deepcopy(DBState.matches),
    )
    save_db()


def undo():
    global previous_state
    if previous_state is None:
        print("No operation to undo.")
        return
    DBState.players[:], DBState.teams[:], DBState.matches[:] = copy.deepcopy(
        previous_state
    )
    save_db()
    print("Last operation undone.")
