# SPDX-License-Identifier: GPL-3.0-or-later

import sqlite3

from datetime import datetime, time
from trueskill import Rating
from db.storage import DB_PATH, DBState

def regenerate_player_days_up_to(date_str):
    cutoff = datetime.combine(datetime.fromisoformat(date_str), time(23, 59, 59))
    matches = DBState.matches

    # Parse match datetimes properly
    matches_sorted = sorted(
        [m for m in matches if datetime.fromisoformat(m.datetime) <= cutoff],
        key=lambda m: datetime.fromisoformat(m.datetime),
    )

    if not matches_sorted:
        print("No matches to apply.")
        return

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Clear existing snapshots for all affected days
    affected_dates = sorted(set(m.datetime.split("T")[0] for m in matches_sorted))
    for d in affected_dates:
        c.execute("DELETE FROM player_days WHERE date = ?", (d,))

    # Reset ratings
    for p in DBState.players:
        p.trueskill = Rating()

    previous_date = None

    for i, match in enumerate(matches_sorted):
        match_date = match.datetime.split("T")[0]
        match.apply_results()

        # Only print once per date
        if match_date != previous_date:
            print(f"Applying matches for {match_date}...")
            previous_date = match_date

        # Save snapshot if:
        # - It's the last match, or
        # - The next match is on a different date
        is_last_match = (i == len(matches_sorted) - 1)
        next_match_date = (
            matches_sorted[i + 1].datetime.split("T")[0]
            if not is_last_match else None
        )
        if is_last_match or next_match_date != match_date:
            for p in DBState.players:
                c.execute(
                    "INSERT INTO player_days (player_id, date, mu, sigma) VALUES (?, ?, ?, ?)",
                    (p.id, match_date, p.mu, p.sigma),
                )
            print(f"Snapshot saved for {match_date}")

    conn.commit()
    conn.close()
    print(f"Regenerated player_days up to {date_str}")


def regenerate_all_player_days():
    """Regenerates player_days for all match dates up to the latest match."""
    if not DBState.matches:
        print("No matches to process.")
        return

    latest_date = max(m.datetime.split("T")[0] for m in DBState.matches)
    regenerate_player_days_up_to(latest_date)

