@echo off
REM ParentEye Client EXE Build Script
REM Builds a production-ready executable that auto-registers and runs without console

setlocal enabledelayedexpansion

echo.
echo ============================================
echo  ParentEye Client - EXE Builder
echo ============================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo ❌ PyInstaller is not installed
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ❌ Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo ✅ PyInstaller is ready

REM Clean previous build
if exist "dist\ParentEye.exe" (
    echo.
    echo Removing previous build...
    rmdir /s /q dist 2>nul
    rmdir /s /q build 2>nul
    del /q ParentEye_Client.spec.bak 2>nul
)

REM Build the EXE
echo.
echo Building ParentEye.exe...
echo.

REM Use the spec file for consistent builds
pyinstaller ParentEye_Client.spec --distpath=dist --buildpath=build

if errorlevel 1 (
    echo.
    echo ❌ Build failed!
    pause
    exit /b 1
)

REM Verify the EXE was created
if exist "dist\ParentEye.exe" (
    echo.
    echo ============================================
    echo ✅ BUILD SUCCESSFUL!
    echo ============================================
    echo.
    echo 📁 Output: dist\ParentEye.exe
    echo 💾 Size: 
    for %%F in ("dist\ParentEye.exe") do echo    %%~zF bytes
    echo.
    echo ✨ Features:
    echo    ✓ No console window
    echo    ✓ Runs with admin privileges
    echo    ✓ Auto-registers device
    echo    ✓ Adds itself to Windows startup
    echo    ✓ All dependencies bundled
    echo.
    echo 🚀 Ready to deploy on child PCs!
    echo.
) else (
    echo.
    echo ❌ Build completed but EXE not found!
    echo.
)

pause

echo.
echo ========================================
echo    BUILD SUCCESSFUL!
echo ========================================
echo.
echo Output: dist\ParentEye_Client.exe
echo.
echo Next Steps:
echo   1. Copy dist\ParentEye_Client.exe to target PCs
echo   2. Also copy .env file for configuration
echo   3. Run as Administrator on child PC
echo.
echo Files ready for distribution:
echo   - dist\ParentEye_Client.exe
echo   - .env (client configuration)
echo.

pause
