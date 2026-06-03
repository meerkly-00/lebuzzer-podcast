@echo off
cd /d "C:\Users\jchal\LeBuzzer"

echo === Removing lock file ===
del /f ".git\index.lock" 2>nul && echo Lock removed. || echo No lock file.

echo.
echo === Staging all files ===
git add -A
if errorlevel 1 (echo git add failed & pause & exit /b 1)

echo.
echo === Committing ===
git commit -m "Deploy: new site design + social kit + favicon assets"
if errorlevel 1 (echo git commit failed & pause & exit /b 1)

echo.
echo === Pushing to origin/main ===
git push origin main
if errorlevel 1 (echo git push failed - check credentials & pause & exit /b 1)

echo.
echo === DONE - Cloudflare Pages will deploy shortly ===
pause
