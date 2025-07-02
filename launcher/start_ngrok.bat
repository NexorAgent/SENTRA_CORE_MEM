@echo off
REM ======== Lancement tunnel ngrok pour SENTRA_CORE_MEM ========
REM Lancer ce script depuis le dossier launcher\

REM Lancer ngrok sur le port 8000
echo [SENTRA_CORE] Démarrage du tunnel ngrok sur le port 8000...
ngrok http 8000

REM Ouvre le dashboard de monitoring ngrok dans le navigateur local
start http://127.0.0.1:4040

REM Garde la fenêtre ouverte
pause
