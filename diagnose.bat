@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo AI Call Center - Quick Diagnostics
echo ==========================================
echo.

echo [1] Docker Containers Status:
echo.
docker-compose ps
echo.

echo [2] Asterisk Status:
echo.
docker exec asterisk asterisk -rx "core show version" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to Asterisk container!
)
echo.

echo [3] SIP Endpoints:
echo.
docker exec asterisk asterisk -rx "pjsip show endpoints" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot query SIP endpoints!
)
echo.

echo [4] SIP Transports:
echo.
docker exec asterisk asterisk -rx "pjsip show transports" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot query SIP transports!
)
echo.

echo [5] Network Information:
echo.
docker network inspect ai-call-center-system_callcenter 2>nul | findstr /i "Containers"
if errorlevel 1 (
    echo WARNING: Network inspection failed or network not found
)
echo.

echo [6] Port Mappings:
echo.
echo Asterisk ports:
docker port asterisk 2>nul
if errorlevel 1 (
    echo WARNING: Cannot get Asterisk port mappings
)
echo.
echo Backend ports:
docker port backend 2>nul
if errorlevel 1 (
    echo WARNING: Cannot get Backend port mappings
)
echo.

echo [7] Backend Health Check:
echo.
curl -s http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo ERROR: Backend health endpoint not responding!
    echo Checking if backend container is running...
    docker ps | findstr backend
) else (
    echo.
    echo ✓ Backend is healthy
)
echo.

echo [8] AGI Connection Test:
echo.
docker exec asterisk sh -c "echo 'test' | nc -w 2 backend 4573" 2>nul
if errorlevel 1 (
    echo WARNING: AGI connection test failed
    echo This may be normal if the AGI server requires specific protocol
) else (
    echo ✓ AGI connection OK
)
echo.

echo [9] Listening Ports on Host:
echo.
echo Port 5060 (SIP):
netstat -an | findstr ":5060" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 5060 not listening
)
echo.
echo Port 8000 (Backend):
netstat -an | findstr ":8000" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 8000 not listening
)
echo.
echo Port 3000 (Dashboard):
netstat -an | findstr ":3000" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 3000 not listening
)
echo.

echo [10] Container Resource Usage:
echo.
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
echo.

echo [11] Recent Logs (Last 10 lines per service):
echo.
echo --- Asterisk Logs ---
docker logs --tail 10 asterisk 2>nul
echo.
echo --- Backend Logs ---
docker logs --tail 10 backend 2>nul
echo.
echo --- Dashboard Logs ---
docker logs --tail 10 dashboard 2>nul
echo.

echo [12] PC IP Address(es) for iPhone Testing:
echo.
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    set ip=!ip:~1!
    echo   - !ip!
)
echo.

echo ==========================================
echo Diagnostics Complete!
echo ==========================================
echo.
echo If you see errors above, try:
echo 1. Restart services: docker-compose restart
echo 2. Check full logs: docker-compose logs
echo 3. Rebuild containers: docker-compose build --no-cache
echo 4. Run full test: fulltest.bat
echo.
pause

