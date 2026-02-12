@echo off
REM ParentEye Setup and Run Script
REM This script helps you set up and run the admin backend server

setlocal enabledelayedexpansion

cls
color 0a

echo.
echo ============================================
echo    ParentEye - Admin Setup & Launch
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)

echo ✅ Python is installed
python --version
echo.

REM Step 1: Check/install dependencies
echo [1/3] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)
echo ✅ Dependencies OK
echo.

REM Step 2: Check .env
echo [2/3] Checking configuration...
if exist ".env" (
    echo ✅ .env file exists
    echo.
    echo Current settings:
    findstr "BACKEND_URL\|MONGODB_URI\|ADMIN_PASSWORD" .env | findstr /v "^REM"
    echo.
    set /p edit="Do you want to edit .env? (y/n): "
    if /i "!edit!"=="y" (
        echo Opening .env in notepad...
        notepad .env
    )
) else (
    if exist ".env.example" (
        echo Creating .env from .env.example...
        copy .env.example .env >nul
        echo ⚠️ Edit .env with your settings before running the server
        pause
        exit /b 0
    ) else (
        echo ❌ .env.example not found
        pause
        exit /b 1
    )
)
echo.

REM Step 3: Start server
echo [3/3] Starting ParentEye backend server...
echo.
echo ============================================
echo    🚀 Backend Server Starting...
echo ============================================
echo.
echo Server URL: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.

python backend.py

pause
