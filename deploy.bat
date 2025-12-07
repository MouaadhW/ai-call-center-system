@echo off
cls
echo.
echo ==========================================
echo   AI CALL CENTER - COMPLETE DEPLOYMENT
echo ==========================================
echo.

echo [1/6] Checking Python...
python --version
if errorlevel 1 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)
echo.

echo [2/6] Installing dependencies...
cd backend
pip install -q fastapi uvicorn websockets edge-tts sqlalchemy
echo ✓ Dependencies installed
echo.

echo [3/6] Initializing database...
python -m db.init_db
echo ✓ Database ready
echo.

echo [4/6] Starting backend services...
start "Backend API" python -c "from api.server import app; import uvicorn; uvicorn.run(app, host='0.0.0.0', port=8000)"
timeout /t 3 >nul
echo ✓ Backend started on port 8000
echo.

echo [5/6] Starting voice system...
start "Voice System" python voicemobile.py
timeout /t 3 >nul
echo ✓ Voice system started on port 8004
echo.

echo [6/6] Starting dashboard...
cd ..\dashboard
start "Dashboard" cmd /k "npm start"
timeout /t 5 >nul
echo ✓ Dashboard starting on port 3000
echo.

echo ==========================================
echo   ✅ DEPLOYMENT COMPLETE!
echo ==========================================
echo.
echo 📱 iPhone Voice Call:
echo    http://192.168.1.19:8004
echo.
echo 💻 PC Voice Call:
echo    http://localhost:8004
echo.
echo 📊 Dashboard:
echo    http://localhost:3000
echo.
echo 🔌 API:
echo    http://localhost:8000
echo.
echo ==========================================
echo.
echo Press any key to open voice interface...
pause >nul
start http://localhost:8004

