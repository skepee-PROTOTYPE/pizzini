@echo off
echo === Git Push Script ===
echo.

echo [1/3] Showing git status...
git status

echo.
echo [2/3] Adding all changes...
git add -A

echo.
echo [3/3] Committing and pushing...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=Fix: Updated Facebook token, added gTTS, disabled Twitter, cleaned up temp files

git commit -m "%commit_msg%"
git push

echo.
echo ✓ Push complete!
pause
