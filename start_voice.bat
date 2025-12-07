@echo off
echo ==========================================
echo AI Call Center - Voice System
echo ==========================================
echo.

echo [1/3] Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install fastapi uvicorn websockets
)

echo [2/3] Starting voice server...
cd backend
start "Voice Server" python voiceproduction.py

echo.
echo [3/3] Waiting for server to start...
timeout /t 5

echo.
echo ==========================================
echo ✅ Voice System Ready!
echo ==========================================
echo.
echo 📱 iPhone: http://192.168.1.19:8004
echo 💻 PC: http://localhost:8004
echo.
echo Press any key to open in browser...
pause >nul
start http://localhost:8004

