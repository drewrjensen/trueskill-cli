# SPDX-License-Identifier: GPL-3.0-or-later

from collections import defaultdict
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from db.storage import DBState
from db.player_days import regenerate_player_days_up_to
from models import Match, Team
from ratings import recalculate_ratings_from, update_ratings
from cli.util import find_player, parse_participants, save


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

        match_id = max((m.id for m in DBState.matches), default=0) + 1
        match = Match(id=match_id)

        for place, team_players in enumerate(resolved, start=1):
            team_id = max((t.id for t in DBState.teams), default=0) + 1
            team = Team(id=team_id, players=team_players)
            DBState.teams.append(team)
            score = scores[place - 1] if len(scores) >= place else None
            match.match_teams.append({"team": team, "place": place, "score": score})

        match.datetime = (
            datetime_override
            if datetime_override and datetime.fromisoformat(datetime_override)
            else datetime.now().isoformat(timespec="minutes")
        )

        DBState.matches.append(match)
        save()
        print(f"Match recorded at {match.datetime}")

        match_date = match.datetime.split("T")[0]
        regenerate_player_days_up_to(match_date)

    except Exception as e:
        print(f"Error adding match: {e}")


def list_matches():
    if not DBState.matches:
        print("No matches recorded.")
        return
    grouped = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for match in DBState.matches:
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
                        + (
                            f" (score: {mt['score']})"
                            if mt["score"] is not None
                            else ""
                        )
                        for mt in match.match_teams
                    )
                    print(
                        f"      {datetime.fromisoformat(match.datetime).strftime('%H:%M')} : {match.id} -> {team_str}"
                    )


def edit_match(match_id_str):
    try:
        match_id = int(match_id_str)
        match = next(m for m in DBState.matches if m.id == match_id)
    except (ValueError, StopIteration):
        print(f"No match found with ID {match_id_str}")
        return

    print(f"Editing match {match.id} ({match.datetime})")
    for i, entry in enumerate(match.match_teams, start=1):
        names = ", ".join(p.name for p in entry["team"].players)
        score_str = f" (score: {entry['score']})" if entry["score"] is not None else ""
        print(f"  {i}. {names}{score_str}")

    player_names = [p.name for p in DBState.players]
    player_completer = WordCompleter(player_names, ignore_case=True)

    try:
        new_input = prompt(
            "Enter new participants (comma-separated, use brackets for teams, optional 'score:') or leave blank to keep: ",
            completer=player_completer,
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
                    team_id = max((t.id for t in DBState.teams), default=0) + 1
                    team = Team(id=team_id, players=team_players)
                    DBState.teams.append(team)
                    score = scores[place - 1] if len(scores) >= place else None
                    match.match_teams.append(
                        {"team": team, "place": place, "score": score}
                    )

        new_dt = input(
            f"Enter new datetime (YYYY-MM-DDTHH:MM) [default: {match.datetime}]: "
        ).strip()
        if new_dt:
            try:
                datetime.fromisoformat(new_dt)
                match.datetime = new_dt
            except ValueError:
                print("Invalid datetime format. Keeping existing time.")

        recalculate_ratings_from(match.datetime)
        save()
        print("Match updated.")

        match_date = match.datetime.split("T")[0]
        regenerate_player_days_up_to(match_date)

    except Exception as e:
        print(f"Failed to edit match: {e}")


def delete_match(match_id_str):
    try:
        match_id = int(match_id_str)
        match = next(m for m in DBState.matches if m.id == match_id)
        match_date = match.datetime.split("T")[0]
        DBState.matches.remove(match)

        recalculate_ratings_from(match.datetime)
        save()
        print(f"Match {match_id} deleted.")

        regenerate_player_days_up_to(match_date)

    except (ValueError, StopIteration):
        print(f"No match found with ID {match_id_str}")
