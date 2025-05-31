@echo off
REM 【Script d'automatisation SENTRA】
REM Usage : sentra\_cycle.bat \<nom\_du\_projet>

SETLOCAL ENABLEDELAYEDEXPANSION

IF "%\~1"=="" (
echo Usage: %\~nx0 ^\<nom\_du\_projet^>
exit /B 1
)

SET PROJET=%\~1
echo ===============================
echo Lancement de la boucle SENTRA pour le projet : !PROJET!
echo ===============================

REM 1) Récupération des fichiers Discord
echo.
echo ---------- Etape 1: Discord Fetcher ----------
python scripts\discord\_fetcher.py !PROJET!
if ERRORLEVEL 1 (
echo Erreur lors de l'execution de discord\_fetcher.py
exit /B 1
)

REM 2) Génération du résumé brut
echo.
echo ---------- Etape 2: Project Resume ----------
python scripts\project\_resume.py !PROJET!
if ERRORLEVEL 1 (
echo Erreur lors de l'execution de project\_resume.py
exit /B 1
)

REM 3) Génération du résumé GPT
echo.
echo ---------- Etape 3: Project Resumer GPT ----------
python scripts\project\_resumer\_gpt.py !PROJET!
if ERRORLEVEL 1 (
echo Erreur lors de l'execution de project\_resumer\_gpt.py
exit /B 1
)

echo.
echo =========== Cycle terminee pour le projet : !PROJET! ===========
ENDLOCAL
