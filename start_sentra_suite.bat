@echo off
chcp 65001 > nul
title 🚀 Lancement complet de SENTRA_CORE_MEM

echo ================================
echo 🔧 LANCEMENT DES MODULES SENTRA
echo ================================

echo.
echo ▶️ [1/6] Lancement du bot Discord...
if exist "launcher\run_discord.bat" (
    call launcher\run_discord.bat
) else (
    echo ❌ Fichier launcher\run_discord.bat introuvable.
)

echo.
echo ▶️ [2/6] Lancement du traducteur automatique...
if exist "launcher\run_auto_translator.bat" (
    call launcher\run_auto_translator.bat
) else (
    echo ❌ Fichier launcher\run_auto_translator.bat introuvable.
)

echo.
echo ▶️ [3/6] Lancement de l’orchestrateur IA...
if exist "launcher\run_orchestrator.bat" (
    call launcher\run_orchestrator.bat
) else (
    echo ❌ Fichier launcher\run_orchestrator.bat introuvable.
)

REM Suppression des étapes 4 et 5 (doublons)
REM echo.
REM echo ▶️ [4/6] Lancement du cycle SENTRA complet...
REM if exist "launcher\sentra_cycle.bat" (
REM     call launcher\sentra_cycle.bat
REM ) else (
REM     echo ❌ Fichier launcher\sentra_cycle.bat introuvable.
REM )

REM echo.
REM echo ▶️ [5/6] Lancement de l’API mémoire (FastAPI)...
REM if exist "launcher\launch_api.bat" (
REM     call launcher\launch_api.bat
REM ) else (
REM     echo ❌ Fichier launcher\launch_api.bat introuvable.
REM )

echo.
echo ▶️ [4/4] Lancement de N8N (automatisation locale)...
cd /d %~dp0n8n
docker compose up -d
cd /d %~dp0

echo.
echo ✅ Tous les modules SENTRA_CORE_MEM sont lancés.
echo.
echo 🌐 Accès à N8N : http://localhost:5678
echo 🌐 Accès à l’API : http://127.0.0.1:8000/status
pause
