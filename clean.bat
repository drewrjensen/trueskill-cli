@echo off
echo Cleaning project...

if exist build rmdir /s /q build
if exist __pycache__ rmdir /s /q __pycache__
if exist *.spec del /q *.spec
if exist venv rmdir /s /q venv

echo Clean complete.
exit /b 0