@echo off
echo Removing temporary scripts...

del /q update_azure_key.bat 2>nul
del /q clean_git_history.bat 2>nul
del /q remove_secrets_from_history.bat 2>nul
del /q cleanup_temp_files.bat 2>nul
del /q AZURE_KEY_REGENERATION.md 2>nul

echo.
echo Committing and pushing...
git add -A
git commit -m "Remove temporary scripts and documentation"
git push

echo.
echo ✓ Done! Code pushed successfully.
pause
