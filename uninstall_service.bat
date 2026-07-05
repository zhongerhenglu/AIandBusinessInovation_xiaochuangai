@echo off
echo ==============================================
echo   Uninstall Super Agent Windows Service
echo ==============================================
echo.

cd /d "%~dp0"

echo 1. Stopping Service...
python windows_service.py stop

echo.
echo 2. Uninstalling Service...
python windows_service.py remove

echo.
echo ==============================================
echo   Service Uninstallation Completed!
echo ==============================================
pause