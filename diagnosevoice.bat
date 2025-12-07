@echo off
echo ==========================================
echo Voice Test Diagnostics
echo ==========================================
echo.

echo [1/6] Checking Python in Docker...
docker exec backend python --version
echo.

echo [2/6] Checking if voicetest.py exists...
docker exec backend ls -la /app/voicetest.py
echo.

echo [3/6] Checking network IPs...
ipconfig | findstr IPv4
echo.

echo [4/6] Checking if port 8003 is listening...
netstat -an | findstr 8003
echo.

echo [5/6] Checking if voicetest process is running...
docker exec backend ps aux | findstr voicetest
echo.

echo [6/6] Testing localhost connection...
curl http://localhost:8003 2>nul || echo Connection failed
echo.

echo ==========================================
echo Diagnostics Complete
echo ==========================================
pause

