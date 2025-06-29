@echo off
REM Should be runnable from any directory; %~dp0 is the 'launcher' folder.
REM Working directory will become repo_root\api before launching the server.
echo === Lancement de l’API mémoire SENTRA ===
cd /d "%~dp0..\api"
start "" cmd /c "uvicorn main:app --host 127.0.0.1 --port 8000 --reload"


