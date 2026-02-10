@echo off
echo.
echo === DEPLOYING FIREBASE FUNCTIONS ===
echo.
echo This will take 2-3 minutes...
echo.

cd /d "%~dp0"

firebase deploy --only functions

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS! Functions deployed!
    echo ========================================
    echo.
    echo Next: Test the manual post
    echo Run: check_status.bat
    echo.
) else (
    echo.
    echo ========================================
    echo DEPLOYMENT FAILED!
    echo ========================================
    echo.
    echo Try these troubleshooting steps:
    echo 1. Check your internet connection
    echo 2. Run: firebase login
    echo 3. Try again
    echo.
)

pause
