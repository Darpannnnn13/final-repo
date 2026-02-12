REM Silent Admin Launcher for ParentEye
REM This script runs ParentEye Client with admin rights and no visible window

if "%1"=="" (
  REM Re-run as admin with elevated privileges
  powershell -Command "Start-Process cmd -ArgumentList '/c %0 elevated' -Verb RunAs -WindowStyle Hidden" >nul 2>&1
  exit /b
)

REM Change to script directory
cd /d "%~dp0"

REM Get the location of ParentEye_Client.exe
set "CLIENT_EXE=%~dp0ParentEye_Client.exe"

REM Run the client silently with admin privileges
start "" /B "%CLIENT_EXE%"

REM Exit silently
exit /b
