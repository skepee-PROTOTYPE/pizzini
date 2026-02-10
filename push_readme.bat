@echo off
echo Committing changes...

git add -A
git commit -m "docs: Remove non-existent website URL, update podcast info"
git push

echo.
echo ✓ Changes pushed!
pause
