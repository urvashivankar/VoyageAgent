@echo off
echo ===================================================
echo Starting TripPilot AI Servers
echo ===================================================

echo.
echo [1/2] Starting Backend Server (FastAPI on Port 8000)...
start "TripPilot Backend" cmd /k "cd backend && python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000"

echo.
echo [2/2] Starting Frontend Server (Port 3000)...
start "TripPilot Frontend" cmd /k "cd frontend && python -m http.server 3000"

echo.
echo ===================================================
echo Servers are starting in new windows!
echo.
echo IMPORTANT: Do NOT open the HTML files directly.
echo Please open your web browser and go exactly to:
echo.
echo http://localhost:3000
echo ===================================================
echo.
pause
