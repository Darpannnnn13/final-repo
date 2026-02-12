@echo off
REM Quick Start Script for Child Monitoring System

echo.
echo ======================================
echo Child Monitoring System - Quick Start
echo ======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if MongoDB is installed
mongod --version >nul 2>&1
if errorlevel 1 (
    echo WARNING: MongoDB is not detected!
    echo Download from: https://www.mongodb.com/try/download/community
    echo.
    echo You can use MongoDB Atlas (cloud) instead:
    echo https://www.mongodb.com/cloud/atlas
    echo.
)

REM Install dependencies
echo Installing Python dependencies...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next steps:
echo.
echo 1. Make sure MongoDB is running:
echo    - Local: mongod
echo    - Cloud: MongoDB Atlas (update MONGO_URI in files)
echo.
echo 2. Start the server:
echo    python backend.py
echo.
echo 3. Install client on child's PC:
echo    python client.py
echo.
echo 4. Open dashboard:
echo    http://localhost:5000
echo.
pause
