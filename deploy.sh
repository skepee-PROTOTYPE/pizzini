#!/bin/bash

# Quick deployment script for Firebase
echo "🔥 Deploying Pizzini Automation to Firebase..."

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Install with: npm install -g firebase-tools"
    exit 1
fi

# Check if logged in
if ! firebase projects:list &> /dev/null; then
    echo "🔑 Please login to Firebase first:"
    firebase login
fi

# Upload config and content
echo "📤 Uploading configuration and content..."
python firebase_setup.py

if [ $? -ne 0 ]; then
    echo "❌ Failed to upload configuration. Please check your setup."
    exit 1
fi

# Deploy functions
echo "🚀 Deploying functions..."
firebase deploy --only functions

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "🔗 Your functions are available at:"
    firebase functions:config:get | grep -o 'https://[^"]*'
    echo ""
    echo "📊 Test your deployment:"
    echo "curl https://your-project-id.cloudfunctions.net/get_status"
else
    echo "❌ Deployment failed. Check the logs above."
    exit 1
fi