@echo off
pyinstaller --onefile --add-data "schemas.sql;." src\main.py --log-level=ERROR >nul
exit /b %errorlevel%