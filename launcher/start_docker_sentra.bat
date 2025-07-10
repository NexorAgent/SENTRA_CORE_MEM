@echo off
REM ======== Build & Run SENTRA_CORE_MEM Docker ========

REM Étape 1 : Build l'image Docker (modifie le nom si besoin)
echo [SENTRA_CORE] Build de l'image Docker...
docker build -t sentra_core_mem:latest .

REM Étape 2 : Supprime les conteneurs stoppés pour éviter les conflits (optionnel)
docker container prune -f

REM Étape 3 : Lance le conteneur en mappant la mémoire
echo [SENTRA_CORE] Lancement du conteneur...
docker run --rm -p 8000:8000 -v %cd%\memoire:/app/memoire sentra_core_mem:latest

REM Pause à la fin si besoin
pause

