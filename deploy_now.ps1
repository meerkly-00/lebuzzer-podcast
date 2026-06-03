# Le Buzzer — deploy script
# Remove stale lock, commit all changes, push to GitHub

Set-Location "C:\Users\jchal\LeBuzzer"

Write-Host "=== Removing lock file ==="
if (Test-Path ".git\index.lock") {
    Remove-Item ".git\index.lock" -Force
    Write-Host "Lock removed."
} else {
    Write-Host "No lock file found."
}

Write-Host ""
Write-Host "=== Staging all files ==="
git add -A
if ($LASTEXITCODE -ne 0) { Write-Host "git add failed"; Read-Host "Press Enter"; exit 1 }

Write-Host ""
Write-Host "=== Committing ==="
git commit -m "Deploy: new site design + social kit + favicon assets"
if ($LASTEXITCODE -ne 0) { Write-Host "git commit failed"; Read-Host "Press Enter"; exit 1 }

Write-Host ""
Write-Host "=== Pushing to origin/main ==="
git push origin main
if ($LASTEXITCODE -ne 0) { Write-Host "git push failed (check credentials)"; Read-Host "Press Enter"; exit 1 }

Write-Host ""
Write-Host "=== DONE — Cloudflare Pages will deploy in ~1 min ==="
Read-Host "Press Enter to close"
