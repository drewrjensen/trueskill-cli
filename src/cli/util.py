# SPDX-License-Identifier: GPL-3.0-or-later

import copy

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


def parse_participants(input_str):
    participants = []
    scores = []
    buffer = ""
    inside_team = False
    tokens = input_str.split()

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("score:"):
            scores = [int(s) for s in token[6:].split(",")]
        else:
            for char in token:
                if char == "[":
                    inside_team = True
                    buffer = ""
                elif char == "]":
                    inside_team = False
                    team = [name.strip() for name in buffer.split(",") if name.strip()]
                    participants.append(team)
                    buffer = ""
                elif char == "," and not inside_team:
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
    DBState.players[:], DBState.teams[:], DBState.matches[:] = copy.deepcopy(previous_state)
    save_db()
    print("Last operation undone.")