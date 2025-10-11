@echo off
REM Quick deployment script for Firebase (Windows)
echo 🔥 Deploying Pizzini Automation to Firebase...

REM Check if Firebase CLI is installed
firebase --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Firebase CLI not found. Install with: npm install -g firebase-tools
    exit /b 1
)

REM Check if logged in
firebase projects:list >nul 2>&1
if errorlevel 1 (
    echo 🔑 Please login to Firebase first:
    firebase login
)

REM Upload config and content
echo 📤 Uploading configuration and content...
python firebase_setup.py

if errorlevel 1 (
    echo ❌ Failed to upload configuration. Please check your setup.
    exit /b 1
)

REM Deploy functions
echo 🚀 Deploying functions...
firebase deploy --only functions

if errorlevel 0 (
    echo ✅ Deployment successful!
    echo.
    echo 📊 Test your deployment:
    echo curl https://your-project-id.cloudfunctions.net/get_status
) else (
    echo ❌ Deployment failed. Check the logs above.
    exit /b 1
)