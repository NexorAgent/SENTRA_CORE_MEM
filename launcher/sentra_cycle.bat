@echo off
echo === Lancement de sentra_cycle.bat ===
cd /d C:\Users\julie\SENTRA_CORE_MEM-main\scripts
set PROJET=SENTRA_CORE_MEM
python discord_fetcher.py
python project_resume.py %PROJET%
python project_resumer_gpt.py %PROJET%
