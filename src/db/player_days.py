# SPDX-License-Identifier: GPL-3.0-or-later

from datetime import datetime
from trueskill import Rating
import sqlite3
from db.storage import DB_PATH


def regenerate_player_days_up_to(date_str, players, matches):
    cutoff = datetime.fromisoformat(date_str)

    matches_sorted = sorted(
        [m for m in matches if datetime.fromisoformat(m.datetime) <= cutoff],
        key=lambda m: m.datetime,
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    match_dates = sorted(set(m.datetime.split("T")[0] for m in matches_sorted))
    for d in match_dates:
        c.execute("DELETE FROM player_days WHERE date = ?", (d,))

    for p in players:
        p.trueskill = Rating()

    current_snapshot_date = None
    for match in matches_sorted:
        match_date = match.datetime.split("T")[0]
        match.apply_results()

        if match_date != current_snapshot_date:
            current_snapshot_date = match_date
            for p in players:
                c.execute(
                    "INSERT INTO player_days (player_id, date, mu, sigma) VALUES (?, ?, ?, ?)",
                    (p.id, match_date, p.mu, p.sigma),
                )

    conn.commit()
    conn.close()
    print(f"Regenerated player days up to {date_str}")


def regenerate_all_player_days():
    from db.storage import players, matches

    today = datetime.now().date().isoformat()
    regenerate_player_days_up_to(today, players, matches)
