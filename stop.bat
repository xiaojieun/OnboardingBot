@echo off
title Stop Services

echo.
echo   Stopping all services...

taskkill /F /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq *uvicorn-backend*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq node.exe" /FI "WINDOWTITLE eq *vite-frontend*" >nul 2>&1

echo   Done.
echo.
pause
