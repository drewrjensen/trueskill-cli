# SPDX-License-Identifier: GPL-3.0-or-later

import db


def rebuild_all_snapshots():
    db.regenerate_all_player_days()
    print("Rebuilt player_days table for all match dates.")
