@echo off
echo Cleaning project...
rmdir /s /q build
rmdir /s /q __pycache__
del /q *.spec
rmdir /s /q venv
echo Clean complete.