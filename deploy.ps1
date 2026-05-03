# Cleanup and Push Script for Multi-Agent Platform (Compatibility Version)

Write-Host "Cleaning up unwanted files..." -ForegroundColor Cyan
if (Test-Path "frontend") { Remove-Item -Recurse -Force "frontend" }

Write-Host "Creating .gitignore to protect your API keys..." -ForegroundColor Cyan
$gitignoreContent = @"
# API Keys and Secrets
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# Python
__pycache__/
*.py[cod]
*$py.class
.venv
venv/
ENV/

# Node
node_modules/
.next/
out/
build/
dist/

# System
.DS_Store
Thumbs.db
"@
$gitignoreContent | Out-File -FilePath ".gitignore" -Encoding ascii

Write-Host "Initializing Git and Pushing to GitHub..." -ForegroundColor Cyan
git init
git add .
git commit -m "feat: complete multi-agent task automation platform with premium UI"
git remote add origin https://github.com/dinesh-kn-0380/Multi-Agent-Task-Automation-Platform.git
git branch -M main
git push -u origin main

Write-Host "DONE! Your code is now live on GitHub." -ForegroundColor Green
