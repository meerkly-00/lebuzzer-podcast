@echo off
cd /d "C:\Users\jchal\LeBuzzer"
del /f ".git\index.lock" 2>nul
del /f ".git\index" 2>nul
git reset HEAD
git add feed.xml
git commit -m "Fix: itunes:email -> prestopodcast@gmail.com pour soumission Spotify"
git pull --rebase origin main
git push origin main
echo.
echo DONE - attends 30 sec puis resoumets sur podcasters.spotify.com
pause
