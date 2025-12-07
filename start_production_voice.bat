@echo off
echo ==========================================
echo Starting Production Voice Interface
echo ==========================================
echo.

echo Starting production voice server in Docker container...
docker exec -d backend python voiceproduction.py

echo.
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo Production Voice Interface is starting!
echo ==========================================
echo.
echo On your PC, open:
echo   http://localhost:8004
echo.
echo On iPhone (same WiFi):
echo   http://192.168.1.19:8004
echo.
echo Production Features:
echo   - Better microphone detection
echo   - Database call recording
echo   - Smart AI responses
echo   - No transfer loops
echo   - Conversation end detection
echo.
echo ==========================================
pause

