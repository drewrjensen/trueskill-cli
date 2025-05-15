# SPDX-License-Identifier: GPL-3.0-or-later

import sqlite3
from datetime import datetime
from db.storage import DB_PATH, DBState

players = DBState.players


def show_rankings_for_date(date_str):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT MAX(date) FROM player_days WHERE date <= ?", (date_str,))
    result = c.fetchone()
    latest_date = result[0] if result and result[0] else None

    if not latest_date:
        print(f"No ranking data found on or before {date_str}")
        conn.close()
        return

    c.execute(
        """
        SELECT p.name, pd.mu, pd.sigma
        FROM player_days pd
        JOIN players p ON pd.player_id = p.id
        WHERE pd.date = ?
        ORDER BY pd.mu DESC
        """,
        (latest_date,),
    )
    ranked_players = c.fetchall()
    conn.close()

    pad_width = len(str(len(ranked_players)))
    longest_name = max(len(name) for name, _, _ in ranked_players)

    print(f"Rankings for {latest_date} (closest to requested: {date_str}):")
    for idx, (name, mu, sigma) in enumerate(ranked_players, start=1):
        print(
            f"({str(idx).rjust(pad_width)}) {name.ljust(longest_name)} - μ={mu:.2f}, σ={sigma:.2f}"
        )


def show_rankings():
    if not players:
        print("No players found.")
        return
    show_rankings_for_date(datetime.now().date().isoformat())
