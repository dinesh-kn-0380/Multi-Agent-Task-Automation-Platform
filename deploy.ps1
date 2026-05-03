# Final Cleanup and Force Push Script

Write-Host "Fixing embedded repository issue..." -ForegroundColor Cyan
if (Test-Path "chatbot-ui-base/.git") { 
    Remove-Item -Recurse -Force "chatbot-ui-base/.git" 
    Write-Host "Removed nested .git folder." -ForegroundColor Yellow
}

Write-Host "Updating repository remote URL..." -ForegroundColor Cyan
git remote set-url origin https://github.com/dinesh-kn-0380/Multi-Agent-Task-Automation-Platform.git

Write-Host "Force adding all files..." -ForegroundColor Cyan
git add .
git commit -m "feat: complete platform with all frontend and backend files"

Write-Host "Pushing to the correct repository..." -ForegroundColor Cyan
git push -u origin main --force

Write-Host "SUCCESS! Check your new repo now." -ForegroundColor Green
