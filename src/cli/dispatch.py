# SPDX-License-Identifier: GPL-3.0-or-later

from db.storage import load_db, save_db, DB_PATH
from db.serialization import export_db, import_db
from cli.players import add_player, list_players, delete_player
from cli.matches import add_match, list_matches, edit_match, delete_match
from cli.rankings import show_rankings, show_rankings_for_date
from cli.util import undo
from cli.snapshots import rebuild_all_snapshots


def run_cli(args):
    # Only load the DB if we're not importing from JSON
    if args.cmd != "import":
        load_db()

    if args.cmd == "players":
        if args.action == "list":
            list_players()
        elif args.action == "add" and args.name:
            add_player(args.name)
        elif args.action == "delete" and args.name:
            delete_player(args.name)

    elif args.cmd == "rankings":
        if hasattr(args, "date") and args.date:
            show_rankings_for_date(args.date)
        else:
            show_rankings()

    elif args.cmd == "matches":
        if args.action == "add" and args.arg:
            add_match(args.arg, args.time)
        elif args.action == "list":
            list_matches()
        elif args.action == "edit" and args.arg:
            edit_match(args.arg)
        elif args.action == "delete" and args.arg:
            delete_match(args.arg)

    elif args.cmd == "undo":
        undo()

    elif args.cmd == "import":
        json_path = args.path if hasattr(args, "path") else "league.json"
        import_db(json_path)
        save_db()
        print(f"DEBUG: Database saved to {DB_PATH}")

    elif args.cmd == "export":
        json_path = args.path if hasattr(args, "path") else "league.json"
        export_db(json_path)

    elif args.cmd == "rebuild-snapshots":
        rebuild_all_snapshots()
