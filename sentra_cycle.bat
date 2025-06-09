@echo off
REM Cycle complet Sentra
cd /d %~dp0

REM 1. Récupère les fichiers Discord
python scripts/discord_fetcher.py

REM 2. Génère le résumé brut
python scripts/project_resume.py SENTRA_CORE

REM 3. Génère le résumé GPT final
python scripts/project_resumer_gpt.py SENTRA_CORE

REM 4. Synchronisation Notion et Discord
python sentra/orchestrator.py sync --target all

REM 5. Commit automatique via CODEX
python scripts/SENTRA_GITOPS.py add .
python scripts/SENTRA_GITOPS.py commit -m "auto: cycle update"
python scripts/SENTRA_GITOPS.py push
