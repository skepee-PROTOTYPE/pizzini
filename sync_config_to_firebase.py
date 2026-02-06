"""
Update Firestore configuration with current config.json
This will sync the local config to Firebase for the scheduled posts
"""
import json
import requests

# Read local config
with open('config.json', 'r') as f:
    config = json.load(f)

print("📝 Uploading configuration to Firebase...")
print(f"   Twitter enabled: {config['social_media']['twitter']['enabled']}")
print(f"   Facebook enabled: {config['social_media']['facebook']['enabled']}")
print(f"   Scheduling enabled: {config['scheduling']['enabled']}")
print()

# Get Firebase project info
with open('firebase.json', 'r') as f:
    firebase_config = json.load(f)

# Use known project ID
project_id = "pizzini-91da9"
print(f"🔥 Firebase Project: {project_id}")

# Try to update via the deployed function
try:
    # You'll need to get your function URL
    # Format: https://us-central1-YOUR_PROJECT.cloudfunctions.net/update_config
    
    if project_id:
        function_url = f"https://us-central1-{project_id}.cloudfunctions.net/update_config"
        print(f"📤 Uploading to: {function_url}")
        
        response = requests.post(function_url, json=config, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Configuration uploaded successfully!")
            print(f"   Response: {result}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            print()
            print("💡 Please run this manually:")
            print(f"   firebase deploy --only functions:update_config")
            print(f"   Then run this script again")
    else:
        print("⚠️  Please update manually:")
        print("   1. Get your function URL from Firebase Console")
        print("   2. POST config.json to: https://YOUR-REGION-YOUR-PROJECT.cloudfunctions.net/update_config")
        
except Exception as e:
    print(f"❌ Error: {e}")
    print()
    print("📋 MANUAL UPDATE INSTRUCTIONS:")
    print("   1. Run: firebase deploy --only functions:update_config")
    print("   2. Get the function URL from Firebase Console")
    print("   3. Use curl or Postman to POST config.json to that URL")
