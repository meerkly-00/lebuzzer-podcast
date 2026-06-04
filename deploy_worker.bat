@echo off
REM ============================================================
REM  LE BUZZER - Deploy the Cloudflare Worker (audio-proxy)
REM
REM  The homepage www.lebuzzer.com is served by this Worker,
REM  NOT by Cloudflare Pages. The Worker proxies site/index.html
REM  from raw.githubusercontent.com. GitHub raw forces a hostile
REM  CSP (default-src 'none'; sandbox) that blocks ALL fonts.
REM
REM  The fix lives in worker\audio-proxy.js (strips that CSP and
REM  sets a permissive one). It only takes effect once the Worker
REM  is redeployed with wrangler. A plain "git push" does NOT
REM  redeploy the Worker - you must run THIS script.
REM ============================================================

cd /d "C:\Users\jchal\LeBuzzer\worker"

echo === Deploying Worker via wrangler ===
echo (Using your cached "wrangler login" session.)
echo.

call npx --yes wrangler@latest deploy
if errorlevel 1 (
  echo.
  echo Worker deploy FAILED.
  echo If it says you are not authenticated, run:  npx wrangler login
  echo then double-click this file again.
  pause
  exit /b 1
)

echo.
echo === Worker deployed. ===
echo The site uses Cloudflare's edge cache (max-age=300), so the new
echo headers may take up to ~5 minutes to appear. To verify:
echo   curl -sI "https://www.lebuzzer.com/?x=1"  ^|  findstr /I "content-security-policy"
echo You should now see "font-src 'self' data:" instead of "sandbox".
echo.
pause
