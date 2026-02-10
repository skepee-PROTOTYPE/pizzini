@echo off
echo Pushing final changes...

git add -A
git commit -m "docs: Remove non-existent website URL, update podcast info"
git push

echo.
echo ✓ All changes pushed!
pause
