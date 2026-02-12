@echo off
REM ParentEye - Complete Deployment Package Creator
REM Creates a ready-to-deploy folder with EXE and configuration

setlocal enabledelayedexpansion
color 0f
cls

echo.
echo ========================================================
echo      ParentEye - Deployment Package Creator
echo ========================================================
echo.

REM Check if dist folder exists
if not exist dist\ (
    echo ERROR: dist folder not found!
    echo.
    echo First, build the executable:
    echo   build_exe.bat
    echo.
    pause
    exit /b 1
)

REM Check if ParentEye_Client.exe exists
if not exist dist\ParentEye_Client.exe (
    echo ERROR: dist\ParentEye_Client.exe not found!
    echo.
    echo Build it first:
    echo   build_exe.bat
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Create configuration:
    echo   python config_client.py --wizard
    echo.
    pause
    exit /b 1
)

REM Create deployment folder
set DEPLOY_FOLDER=ParentEye_Deploy_%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%
set DEPLOY_FOLDER=!DEPLOY_FOLDER: =0!

echo Creating deployment package: %DEPLOY_FOLDER%
echo.

if exist "%DEPLOY_FOLDER%" (
    echo Removing existing deployment folder...
    rmdir /s /q "%DEPLOY_FOLDER%"
)

echo Creating folders...
mkdir "%DEPLOY_FOLDER%"
mkdir "%DEPLOY_FOLDER%\exe"
mkdir "%DEPLOY_FOLDER%\docs"

echo Copying files...

REM Copy executable
copy dist\ParentEye_Client.exe "%DEPLOY_FOLDER%\exe\" >nul
echo   ✓ ParentEye_Client.exe

REM Copy configuration
copy .env "%DEPLOY_FOLDER%\exe\.env" >nul
echo   ✓ Configuration (.env)

REM Copy documentation
copy DEPLOYMENT_GUIDE.md "%DEPLOY_FOLDER%\docs\" >nul
copy REMOTE_DEPLOYMENT.md "%DEPLOY_FOLDER%\docs\" >nul
copy QUICK_START_COMPLETE.md "%DEPLOY_FOLDER%\docs\" >nul
copy DEPLOYMENT_CHECKLIST.md "%DEPLOY_FOLDER%\docs\" >nul
echo   ✓ Documentation files

REM Copy batch helpers
copy run_client_as_admin.bat "%DEPLOY_FOLDER%\exe\" >nul
echo   ✓ Helper scripts

REM Create deployment README
echo. > "%DEPLOY_FOLDER%\README.txt"
echo PARENEYE - DEPLOYMENT PACKAGE >> "%DEPLOY_FOLDER%\README.txt"
echo. >> "%DEPLOY_FOLDER%\README.txt"
echo Contents: >> "%DEPLOY_FOLDER%\README.txt"
echo  • exe/ - ParentEye_Client.exe (run this on child PC) >> "%DEPLOY_FOLDER%\README.txt"
echo  • docs/ - Setup and troubleshooting guides >> "%DEPLOY_FOLDER%\README.txt"
echo. >> "%DEPLOY_FOLDER%\README.txt"
echo To Deploy: >> "%DEPLOY_FOLDER%\README.txt"
echo 1. Copy exe\ folder to child PC >> "%DEPLOY_FOLDER%\README.txt"
echo 2. Right-click ParentEye_Client.exe >> "%DEPLOY_FOLDER%\README.txt"
echo 3. Select "Run as Administrator" >> "%DEPLOY_FOLDER%\README.txt"
echo. >> "%DEPLOY_FOLDER%\README.txt"
echo For help, see docs\ folder. >> "%DEPLOY_FOLDER%\README.txt"
echo. >> "%DEPLOY_FOLDER%\README.txt"
timeout /t 0

REM Create zip file for easy distribution (optional)
cd /d "%DEPLOY_FOLDER%"
set DEPLOY_ZIP=..\%DEPLOY_FOLDER%.zip
cd ..

cls
color 0a

echo.
echo ========================================================
echo      DEPLOYMENT PACKAGE CREATED!
echo ========================================================
echo.
echo Location: %CD%\%DEPLOY_FOLDER%\
echo.
echo Contents:
echo   • exe\ParentEye_Client.exe    (174 MB executable)
echo   • exe\.env                     (Configuration)
echo   • exe\run_client_as_admin.bat  (Admin launcher)
echo   • docs\*.md                    (Guides)
echo.
echo Created at: %date% %time%
echo.
echo Distribution:
echo   1. Copy %DEPLOY_FOLDER%\ to USB/Cloud
echo   2. Share with parents/administrators
echo   3. Follow instructions in README.txt
echo.
echo To Deploy on Child PC:
echo   1. Copy exe\ folder
echo   2. Right-click ParentEye_Client.exe
echo   3. Run as Administrator
echo.
echo Features:
echo   • Standalone - no Python needed
echo   • Requires admin for blocking features
echo   • Runs in background
echo   • Auto-connects to backend
echo   • Monitoring starts immediately
echo.
echo ========================================================
echo.

REM Open folder
start "" "%DEPLOY_FOLDER%"

pause
