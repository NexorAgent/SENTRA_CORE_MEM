@echo off
REM This script should work from any directory.
REM %~dp0 points to the 'launcher' folder inside the repository root.
REM Working directory will become repo_root\scripts before running Python.
echo === Lancement de run_discord.bat ===
start "" cmd /c "cd /d "%~dp0..\scripts" && python discord_bot.py"
