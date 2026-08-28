$env:PATH += ";C:\Program Files\Git\cmd"
$repo = "C:\Users\Admin\OneDrive\Desktop\ECOSORT_AI"

Write-Host "=== Checking git ===" -ForegroundColor Cyan
git --version

Write-Host "`n=== Git Status ===" -ForegroundColor Cyan
git -C $repo status

Write-Host "`n=== Setting user config ===" -ForegroundColor Cyan
git -C $repo config user.name "namshijoon29"
git -C $repo config user.email "namshijoon29@users.noreply.github.com"

Write-Host "`n=== Staging all files ===" -ForegroundColor Cyan
git -C $repo add .
git -C $repo status

Write-Host "`n=== Committing ===" -ForegroundColor Cyan
git -C $repo commit -m "Initial commit: EcoSort AI project"

Write-Host "`n=== Setting branch to main ===" -ForegroundColor Cyan
git -C $repo branch -M main

Write-Host "`n=== Pushing to GitHub ===" -ForegroundColor Cyan
git -C $repo push -u origin main

Write-Host "`n=== Done ===" -ForegroundColor Green
