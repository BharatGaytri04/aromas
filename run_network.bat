@echo off
echo ============================================================
echo Django Development Server - Network Access
echo ============================================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :found
)
:found
set IP=%IP:~1%

echo Your local IP address: %IP%
echo.
echo To access from another device on the same network:
echo   http://%IP%:8000
echo.
echo To access from this device:
echo   http://127.0.0.1:8000
echo.
echo ============================================================
echo Starting server... (Press Ctrl+C to stop)
echo ============================================================
echo.

python manage.py runserver 0.0.0.0:8000

