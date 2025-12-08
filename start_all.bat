@echo off
echo ========================================
echo AI Call Center System - Quick Start
echo ========================================
echo.

echo [1/5] Starting Docker services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start Docker services
    pause
    exit /b 1
)

echo [2/5] Waiting for services to start...
timeout /t 10 /nobreak >nul

echo [3/5] Installing Edge-TTS (for natural voice)...
docker exec backend pip install -q edge-tts
if errorlevel 1 (
    echo WARNING: Edge-TTS installation failed, but continuing...
)

echo [4/5] Initializing database...
docker exec backend python -m db.init_db
if errorlevel 1 (
    echo WARNING: Database initialization failed, but continuing...
)

echo [5/5] Starting voice interface...
docker exec -d backend python voiceproduction.py
if errorlevel 1 (
    echo ERROR: Failed to start voice interface
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ System Started Successfully!
echo ========================================
echo.
echo 📱 Voice Interface: http://localhost:8004
echo 💬 Web Chat Test: http://localhost:8001
echo 📊 Dashboard: http://localhost:3000
echo.
echo 💡 Tips:
echo    - Open http://localhost:8004 in your browser
echo    - Click "Start Call" and allow microphone access
echo    - Speak naturally - the AI will understand!
echo.
echo Press any key to exit...
pause >nul

