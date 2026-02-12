@echo off
REM Setup ParentEye Client for Auto-Start (Windows)
REM This script sets up the client to run automatically on startup without any user action

echo.
echo ========================================
echo ParentEye Auto-Start Setup
echo ========================================
echo.

REM Get admin rights
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if '%errorlevel%' NEQ '0' (
  echo This script requires Administrator privileges!
  echo Please right-click this file and select "Run as administrator"
  pause
  exit /b 1
)

REM Define paths
set "STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
set "SOURCE_VBS=%~dp0ParentEye_Silent_Admin.vbs"
set "DEST_VBS=%STARTUP_FOLDER%\ParentEye.vbs"

echo.
echo Setting up auto-start for ParentEye...
echo.

REM Check if source file exists
if not exist "%SOURCE_VBS%" (
  echo ERROR: ParentEye_Silent_Admin.vbs not found!
  echo Make sure you're running this from the ParentEye directory.
  pause
  exit /b 1
)

REM Copy VBScript to startup folder
echo Copying ParentEye launcher to Startup folder...
copy "%SOURCE_VBS%" "%DEST_VBS%" /Y >nul

if errorlevel 1 (
  echo ERROR: Failed to copy file to Startup folder
  echo Make sure you have permissions to write to: %STARTUP_FOLDER%
  pause
  exit /b 1
)

echo.
echo ========================================
echo ✅ SUCCESS!
echo ========================================
echo.
echo ParentEye will now:
echo   ✓ Start automatically on next boot
echo   ✓ Run with Administrator privileges
echo   ✓ Show NO visible window
echo   ✓ Connect to: http://192.168.0.104:5000
echo.
echo Location: %DEST_VBS%
echo.
echo You can remove it anytime by deleting:
echo   %DEST_VBS%
echo.
pause
