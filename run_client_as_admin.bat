@echo off
echo ================================================
echo   ParentEye Client - Running as Administrator
echo ================================================
echo.
echo Starting client with elevated privileges...
echo This is required for website blocking features.
echo.

cd /d "%~dp0"
python client.py

pause
