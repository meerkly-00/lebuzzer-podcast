@echo off
cd /d "C:\Users\jchal\LeBuzzer"

echo === Staging changes ===
git add site/index.html
if errorlevel 1 (echo git add failed & pause & exit /b 1)

echo.
echo === Committing ===
git commit -m "Deploy: replace index.html with Claude Design template (Landing.html)"
if errorlevel 1 (echo git commit failed & pause & exit /b 1)

echo.
echo === Pulling rebase ===
git pull --rebase origin main
if errorlevel 1 (echo git pull failed & pause & exit /b 1)

echo.
echo === Pushing to origin/main ===
git push origin main
if errorlevel 1 (echo git push failed & pause & exit /b 1)

echo.
echo === DONE - Cloudflare Pages deploying... ===
pause
