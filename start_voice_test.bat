@echo off
echo ==========================================
echo Starting AI Voice Call Test Interface
echo ==========================================
echo.

echo Starting voice test server in Docker container...
docker exec -d backend python voicetest.py

echo.
echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo ==========================================
echo Voice Test Interface is starting!
echo ==========================================
echo.
echo On your PC, open:
echo   http://localhost:8003
echo.
echo On iPhone (same WiFi):
echo   http://YOUR_IP:8003
echo   (Check your IP with: ipconfig)
echo.
echo Instructions:
echo   1. Click "Start Call"
echo   2. Allow microphone access
echo   3. Wait for AI greeting
echo   4. Speak your question
echo   5. Listen to AI response!
echo.
echo ==========================================
pause

