# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of the TrueSkill CLI project.
#
# Copyright (C) 2025 Drew Jensen
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
from argparse import Namespace

VERSION = "v2.0.0"


def main():
    parser = argparse.ArgumentParser(
        description="TrueSkill CLI - A command-line interface for TrueSkill rating system"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    # Add more arguments and subcommands as needed
    args: Namespace = parser.parse_args()
    # Handle the parsed arguments and execute the appropriate functionality
    print(f"TrueSkill CLI {VERSION} - Arguments: {args}")


if __name__ == "__main__":
    main()
