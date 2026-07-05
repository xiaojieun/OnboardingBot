@echo off
title OnboardingBot - Quick Start

echo.
echo   OnboardingBot - Quick Start
echo   ===========================

set "PROJECT_DIR=%~dp0"
set "VENV_PYTHON=%PROJECT_DIR%.venv\Scripts\python.exe"
set "VENV_PIP=%PROJECT_DIR%.venv\Scripts\pip.exe"

if not exist "%VENV_PYTHON%" (
    echo   [ERROR] .venv not found, creating...
    python -m venv "%PROJECT_DIR%.venv"
    "%VENV_PIP%" install -r "%PROJECT_DIR%requirements.txt"
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo   [ERROR] Node.js not found
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo   [Frontend] Installing dependencies...
    cd frontend
    call npm install
    cd ..
)

echo   [Backend] Starting on http://localhost:8000 ...
start "uvicorn-backend" /MIN cmd /c "cd /d %PROJECT_DIR%backend && set PYTHONPATH=%PROJECT_DIR%backend && "%VENV_PYTHON%" -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000"

timeout /t 3 /nobreak >nul

echo   [Frontend] Starting on http://localhost:5173 ...
start "vite-frontend" /MIN cmd /c "cd /d %PROJECT_DIR%frontend && npm run dev"

echo.
echo   Done!
echo   Backend API Docs : http://localhost:8000/docs
echo   Frontend         : http://localhost:5173
echo.
echo   Press any key to open browser...
pause >nul

start http://localhost:5173
