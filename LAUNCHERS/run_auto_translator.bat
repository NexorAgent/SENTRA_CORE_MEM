@echo off
cd /d "%~dp0"
set /p filename=Nom du fichier source dans /logs (ex: resume sentra.txt) :
if "%filename%"=="" (
    set filename=resume_translated.txt
)

echo [ZIA🦋] Traitement du fichier : logs\\%filename%
python scripts\\run_auto_translator.py -i "%cd%\\logs\\%filename%"
pause
