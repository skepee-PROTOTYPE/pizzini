@echo off
echo Pushing final changes...

git add -A
git commit -m "docs: Add Spotify link and display podcast cover image in README"
git push

echo.
echo ✓ All changes pushed!
pause
