@echo off
REM Build Client Executable for ParentEye
echo ========================================
echo Building ParentEye Client Executable
echo ========================================
echo.

REM Clean previous builds
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "client.spec" del /f "client.spec"

echo Cleaning previous builds...
echo.

REM Build the executable with NO CONSOLE WINDOW
echo Building executable (No console window)...
python -m PyInstaller --onefile --windowed ^
  --name="ParentEye_Client" ^
  --icon=NONE ^
  --add-data ".env;." ^
  --hidden-import=pymongo ^
  --hidden-import=pynput ^
  --hidden-import=psutil ^
  --hidden-import=requests ^
  --hidden-import=dotenv ^
  client.py

echo.
echo ========================================
if exist "dist\ParentEye_Client.exe" (
  echo ✅ Build successful!
  echo.
  echo Executable location:
  echo %cd%\dist\ParentEye_Client.exe
  echo.
  echo File size:
  dir "dist\ParentEye_Client.exe" | find "ParentEye_Client.exe"
  echo.
  echo You can now copy ParentEye_Client.exe to any PC!
) else (
  echo ❌ Build failed! Check errors above.
)
echo ========================================
pause
