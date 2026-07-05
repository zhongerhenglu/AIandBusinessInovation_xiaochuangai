@echo off
chcp 65001 >nul
echo Starting Super Agent Background Service...
echo.
echo Service will run in background and send factor reports every 4 hours.
echo Reports will be sent at: 08:00, 12:00, 16:00, 20:00, 24:00
echo.
echo Press Ctrl+C to stop the service.
echo.
python start_background_service.py
pause