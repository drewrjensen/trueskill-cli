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

import argparse
from cli import run_cli
from db import init_db, set_db_path

VERSION = "v1.3.0"


def main():
    parser = argparse.ArgumentParser(description="TrueSkill League CLI")
    parser.add_argument(
        "--version", action="version", version=f"TrueSkill CLI {VERSION}"
    )
    parser.add_argument(
        "--db-path",
        default="league.db",
        help="Path to database file (default: league.db)",
    )
    sub = parser.add_subparsers(dest="cmd", help="Primary commands")

    # players
    players_parser = sub.add_parser("players", help="Manage players")
    players_parser.add_argument(
        "action",
        choices=["list", "add", "delete"],
        nargs="?",
        default="list",
        help="Action to perform",
    )
    players_parser.add_argument("name", nargs="?", help="Player name(s)")

    # rankings
    rankings_parser = sub.add_parser("rankings", help="Show current player rankings")
    rankings_parser.add_argument(
        "--date", help="Show rankings snapshot for specific date (YYYY-MM-DD)"
    )

    # matches
    matches_parser = sub.add_parser("matches", help="Manage matches")
    matches_parser.add_argument(
        "action",
        choices=["add", "list", "edit", "delete"],
        nargs="?",
        default="list",
        help="Action to perform",
    )
    matches_parser.add_argument(
        "arg",
        nargs="?",
        help="Argument for action (participants for add, match_id for edit/delete)",
    )
    matches_parser.add_argument(
        "--time", help="Optional ISO datetime (e.g., 2025-04-27T14:30) for matches add"
    )
    matches_parser.add_argument(
        "--scores", help="Comma-separated numeric scores for each team (e.g. 20,15,10)"
    )

    # undo
    sub.add_parser("undo", help="Undo last operation")

    # import/export
    import_parser = sub.add_parser(
        "import", help="Import database from JSON (regenerates player_days if missing)"
    )
    import_parser.add_argument(
        "path",
        nargs="?",
        default="league.json",
        help="Path to JSON file (default: league.json)",
    )

    export_parser = sub.add_parser(
        "export", help="Export database to JSON (includes player_days if available)"
    )
    export_parser.add_argument(
        "path",
        nargs="?",
        default="league.json",
        help="Path to export JSON file (default: league.json)",
    )

    # rebuild snapshots
    sub.add_parser(
        "rebuild-snapshots", help="Regenerate player_days for all unique match dates"
    )

    args = parser.parse_args()

    set_db_path(args.db_path)
    init_db()

    if args.cmd is None:
        parser.print_help()
    else:
        run_cli(args)


if __name__ == "__main__":
    main()
