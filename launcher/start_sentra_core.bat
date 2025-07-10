@echo off
title 🚀 Lancement SENTRA_CORE_MEM
cd /d C:\SENTRA_CORE

echo.
echo 🔁 [1/4] Vérification de Docker...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker n'est pas lancé. Merci de le démarrer manuellement.
    pause
    exit /b
)

echo ✅ Docker est actif.
echo.

echo 🚀 [2/4] Lancement de N8N...
cd n8n
docker compose up -d
cd..

echo 🧠 [3/4] Lancement du BOT Discord...
start "" "C:\SENTRA_CORE\discord_bot\launch_bot.bat"

echo 🌐 [4/4] Lancement de l'API FastAPI...
start "" "C:\SENTRA_CORE\launcher\launch_api.bat"

echo.
echo ✅ Tous les services SENTRA_CORE sont lancés.
echo 🔗 Accès à n8n : http://localhost:5678
pause
