@echo off
echo ==========================================
echo   🚀 STARTING MULTI-AGENT PLATFORM 🚀
echo ==========================================

:: Start Backend in a new window
echo [1/2] Starting Python Backend...
start cmd /k "python run.py"

:: Wait a moment for backend to initialize
timeout /t 3 /nobreak > nul

:: Start Frontend in a new window
echo [2/2] Starting Next.js Frontend...
cd chatbot-ui-base
start cmd /k "npm run dev"

echo ==========================================
echo ✅ All systems starting! Check the new windows.
echo Frontend will be at: http://localhost:3001
echo ==========================================
pause
