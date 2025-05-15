#!/bin/bash
source venv/bin/activate
pyinstaller --onefile \
  --hidden-import=trueskill \
  --add-data "schemas.sql:." \
  src/main.py