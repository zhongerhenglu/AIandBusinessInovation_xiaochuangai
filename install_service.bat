@echo off
echo ==============================================
echo   Install Super Agent Windows Service
echo ==============================================
echo.

cd /d "%~dp0"

echo 1. Installing pywin32...
pip install pywin32

echo.
echo 2. Installing Super Agent Service...
python windows_service.py install

echo.
echo 3. Starting Service...
python windows_service.py start

echo.
echo ==============================================
echo   Service Installation Completed!
echo ==============================================
echo.
echo To check service status:
echo   python windows_service.py status
echo.
echo To stop service:
echo   python windows_service.py stop
echo.
echo To uninstall service:
echo   python windows_service.py remove
echo.
pause