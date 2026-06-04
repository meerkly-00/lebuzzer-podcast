@echo off
cd /d "C:\Users\jchal\LeBuzzer"

echo === Removing lock + corrupted index ===
del /f ".git\index.lock" 2>nul
del /f ".git\index" 2>nul

echo === Rebuilding index from HEAD ===
git reset HEAD
if errorlevel 1 (echo git reset failed & pause & exit /b 1)

echo === Staging the real fix (worker) + site files ===
git add worker\audio-proxy.js site\index.html site\_headers deploy_worker.bat repair_and_push.bat
if errorlevel 1 (echo git add failed & pause & exit /b 1)

echo === Committing ===
git commit -m "Fix fonts: strip GitHub-raw CSP/sandbox in Worker proxy"
if errorlevel 1 (echo Nothing new to commit - continuing to push anyway)

echo === Pull rebase ===
git pull --rebase origin main

echo === Push ===
git push origin main
if errorlevel 1 (echo Push failed & pause & exit /b 1)

echo.
echo ============================================================
echo  GIT PUSH DONE.
echo.
echo  IMPORTANT: the homepage is served by a Cloudflare WORKER,
echo  not Cloudflare Pages. The font fix lives in the Worker and
echo  only goes live after you DEPLOY THE WORKER.
echo.
echo  --^> Now double-click:  deploy_worker.bat
echo ============================================================
pause
