@echo off
echo ==========================================
echo Starting AI Call Center Web Test Interface
echo ==========================================
echo.

echo Starting web test server in Docker container...
docker exec -it backend python web_test.py

echo.
echo ==========================================
echo Web Test Interface should be running!
echo ==========================================
echo.
echo Open in your browser: http://localhost:8001
echo.
pause

