# SPDX-License-Identifier: GPL-3.0-or-later

from db.player_days import regenerate_all_player_days

def rebuild_all_snapshots():
    regenerate_all_player_days()
    print("Rebuilt player_days table for all match dates.")
