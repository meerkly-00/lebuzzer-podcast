@echo off
cd /d "C:\Users\jchal\LeBuzzer"

del /f ".git\index.lock" 2>nul
del /f ".git\index" 2>nul
git reset HEAD

git add -A
git commit -m "Fix lecteur audio + proxy /audio/, SEO, NFL, feed valide"
git pull --rebase origin main
git push origin main
if errorlevel 1 (echo Push failed & pause & exit /b 1)

echo.
echo ============================================================
echo  DONE. Lance deploy_worker.bat ensuite.
echo ============================================================
pause
