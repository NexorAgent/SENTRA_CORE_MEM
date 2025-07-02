@echo off
cd /d %~dp0

echo === MERGE DEV -> MAIN ===
git checkout main
git pull origin main
git merge dev
git push origin main
git checkout dev

echo ✅ Merge terminé avec succès.
pause
