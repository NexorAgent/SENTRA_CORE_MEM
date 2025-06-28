@echo off
echo === Lancement de l’API mémoire SENTRA ===
cd /d C:\Users\julie\SENTRA_CORE_MEM-main\api
start "" cmd /c "uvicorn main:app --host 127.0.0.1 --port 8000 --reload"


