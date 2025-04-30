@echo off
py -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies with pip notices suppressed
venv\Scripts\pip install --disable-pip-version-check -r requirements.txt 2>nul
exit /b %errorlevel%