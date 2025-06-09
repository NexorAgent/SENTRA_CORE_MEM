@echo off
cd /d %~dp0\..
echo ============================
echo     SENTRA LAUNCHER
echo ============================
echo 1. Lancer l'API FastAPI (Uvicorn)
echo 2. Lancer le Bot Discord
echo 3. Lancer la Synchro Notion
echo 0. Quitter
echo ============================
set /p choix=Votre choix [0-3] :

if "%choix%"=="1" (
    start cmd /k "uvicorn scripts.api_sentra:app --host 0.0.0.0 --port 8000"
    goto fin
)
if "%choix%"=="2" (
    start cmd /k "python scripts/discord_bot.py"
    goto fin
)
if "%choix%"=="3" (
    start cmd /k "python scripts/agent_notion.py"
    goto fin
)
if "%choix%"=="0" (
    exit
)
:fin
pause
