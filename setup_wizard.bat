@echo off
REM ParentEye - Complete Setup Wizard
REM This guides through the entire setup process

color 0f
cls

:menu
echo.
echo ========================================
echo      ParentEye - Setup Wizard
echo ========================================
echo.
echo What would you like to do?
echo.
echo 1) Configure Client for Remote Backend
echo 2) Test Backend Connection
echo 3) Build Executable (EXE)
echo 4) View Deployment Guide
echo 5) Exit
echo.
set /p choice="Enter choice (1-5): "

if "%choice%"=="1" goto config
if "%choice%"=="2" goto test
if "%choice%"=="3" goto build
if "%choice%"=="4" goto guide
if "%choice%"=="5" goto end
echo Invalid choice!
timeout /t 2
goto menu

:config
cls
color 0a
echo.
echo Launching configuration wizard...
echo.
python config_client.py --wizard
timeout /t 5
goto menu

:test
cls
color 0e
echo.
echo Testing backend connection...
echo.
python test_connection.py
pause
goto menu

:build
cls
color 09
echo.
echo Building executable...
echo.
call build_exe.bat
goto menu

:guide
cls
color 0f
echo.
echo Opening Deployment Guide...
echo.
type DEPLOYMENT_GUIDE.md | more
pause
goto menu

:end
cls
echo.
echo Goodbye!
echo.
