@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo AI Call Center - Complete Test Suite
echo ==========================================
echo.

REM ==========================================
REM PHASE 1: Clean Start & Build
REM ==========================================
echo [PHASE 1] Starting Services...
echo.

echo Step 1.1: Stopping existing containers...
docker-compose down -v
if errorlevel 1 (
    echo WARNING: docker-compose down failed, continuing anyway...
)
echo.

echo Step 1.2: Building containers (this may take 5-10 minutes)...
docker-compose build --no-cache
if errorlevel 1 (
    echo ERROR: Build failed! Check the error messages above.
    pause
    exit /b 1
)
echo.

echo Step 1.3: Starting services...
docker-compose up -d
if errorlevel 1 (
    echo ERROR: Failed to start services! Check the error messages above.
    pause
    exit /b 1
)
echo.

echo Step 1.4: Waiting for services to initialize (15 seconds)...
timeout /t 15 /nobreak >nul
echo.

echo Step 1.5: Checking container status...
docker-compose ps
echo.

REM ==========================================
REM PHASE 2: Database Initialization
REM ==========================================
echo [PHASE 2] Initializing Database...
echo.

docker exec backend python -m db.init_db
if errorlevel 1 (
    echo WARNING: Database initialization may have failed. Trying with -it flag...
    docker exec -it backend python -m db.init_db
)
echo.

REM ==========================================
REM PHASE 3: Backend API Testing
REM ==========================================
echo [PHASE 3] Testing Backend API...
echo.

echo Step 3.1: Testing health endpoint...
curl -s http://localhost:8000/health
if errorlevel 1 (
    echo ERROR: Health endpoint not responding!
    echo Checking if backend container is running...
    docker ps | findstr backend
) else (
    echo.
    echo ✓ Health endpoint OK
)
echo.

echo Step 3.2: Testing analytics endpoint...
curl -s http://localhost:8000/api/analytics
if errorlevel 1 (
    echo WARNING: Analytics endpoint not responding (may need database initialization)
) else (
    echo.
    echo ✓ Analytics endpoint OK
)
echo.

REM ==========================================
REM PHASE 4: Asterisk Testing
REM ==========================================
echo [PHASE 4] Testing Asterisk...
echo.

echo Step 4.1: Checking Asterisk version...
docker exec asterisk asterisk -rx "core show version" 2>nul
if errorlevel 1 (
    echo ERROR: Cannot connect to Asterisk!
) else (
    echo ✓ Asterisk is running
)
echo.

echo Step 4.2: Checking SIP endpoints...
docker exec asterisk asterisk -rx "pjsip show endpoints" 2>nul
if errorlevel 1 (
    echo WARNING: Cannot query endpoints
) else (
    echo ✓ Endpoints query OK
)
echo.

echo Step 4.3: Checking SIP transports...
docker exec asterisk asterisk -rx "pjsip show transports" 2>nul
if errorlevel 1 (
    echo WARNING: Cannot query transports
) else (
    echo ✓ Transports query OK
)
echo.

REM ==========================================
REM PHASE 5: AGI Connection Testing
REM ==========================================
echo [PHASE 5] Testing AGI Connection...
echo.

echo Step 5.1: Testing AGI server connectivity...
docker exec asterisk sh -c "echo 'test' | nc -w 2 backend 4573" 2>nul
if errorlevel 1 (
    echo WARNING: AGI connection test failed (this may be normal if server requires specific protocol)
    echo Checking if backend AGI port is listening...
    docker exec backend netstat -an | findstr "4573" 2>nul
) else (
    echo ✓ AGI connection OK
)
echo.

REM ==========================================
REM PHASE 6: Network Port Testing
REM ==========================================
echo [PHASE 6] Checking Network Ports...
echo.

echo Step 6.1: Checking port 5060 (SIP)...
netstat -an | findstr ":5060" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 5060 not found in LISTENING state
) else (
    echo ✓ Port 5060 (SIP) is listening
)
echo.

echo Step 6.2: Checking port 8000 (Backend API)...
netstat -an | findstr ":8000" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 8000 not found in LISTENING state
) else (
    echo ✓ Port 8000 (Backend API) is listening
)
echo.

echo Step 6.3: Checking port 3000 (Dashboard)...
netstat -an | findstr ":3000" | findstr "LISTENING"
if errorlevel 1 (
    echo WARNING: Port 3000 not found in LISTENING state
) else (
    echo ✓ Port 3000 (Dashboard) is listening
)
echo.

REM ==========================================
REM PHASE 7: Get PC IP Address
REM ==========================================
echo [PHASE 7] Network Configuration...
echo.

echo Step 7.1: Your PC's IP address(es) for iPhone testing:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do (
    set ip=%%a
    set ip=!ip:~1!
    echo   - !ip!
)
echo.

REM ==========================================
REM SUMMARY & NEXT STEPS
REM ==========================================
echo ==========================================
echo Test Complete!
echo ==========================================
echo.
echo Container Status:
docker-compose ps
echo.
echo ==========================================
echo Next Steps:
echo ==========================================
echo.
echo 1. PC SIP CLIENT (MicroSIP):
echo    - Download: https://www.microsip.org/downloads
echo    - Configure:
echo      * Server: localhost
echo      * Port: 5060
echo      * Username: 6002
echo      * Password: 6002
echo      * Transport: UDP
echo    - Test calls:
echo      * Dial 200 for echo test
echo      * Dial 100 for AI agent
echo.
echo 2. IPHONE SIP CLIENT (Zoiper):
echo    - Install Zoiper Lite from App Store
echo    - Configure:
echo      * Domain: [Your PC IP from above]
echo      * Port: 5060
echo      * Username: 6001
echo      * Password: 6001
echo      * Transport: UDP
echo      * STUN: stun.l.google.com:19302
echo    - Test calls:
echo      * Dial 200 for echo test
echo      * Dial 100 for AI agent
echo.
echo 3. DASHBOARD:
echo    - Open: http://localhost:3000
echo    - View calls, analytics, and settings
echo.
echo 4. MONITORING:
echo    - Asterisk CLI: docker exec -it asterisk asterisk -rvvvv
echo    - Backend logs: docker logs backend -f
echo    - All logs: docker-compose logs -f
echo.
echo ==========================================
echo SUCCESS CHECKLIST:
echo ==========================================
echo.
echo After manual testing, verify:
echo [ ] All containers running (docker-compose ps)
echo [ ] Backend API responding (http://localhost:8000/health)
echo [ ] Dashboard accessible (http://localhost:3000)
echo [ ] Asterisk endpoints showing (pjsip show endpoints)
echo [ ] MicroSIP registered on PC
echo [ ] Echo test (200) working from PC
echo [ ] AI agent (100) working from PC
echo [ ] iPhone can access PC (http://[IP]:8000/health)
echo [ ] Zoiper registered on iPhone
echo [ ] Calls working from iPhone
echo.
echo ==========================================
echo.

REM ==========================================
REM OPTIONAL: Open Dashboard
REM ==========================================
set /p open_dashboard="Open dashboard in browser? (y/n): "
if /i "!open_dashboard!"=="y" (
    start http://localhost:3000
)

echo.
echo Test script completed. Press any key to exit...
pause >nul

