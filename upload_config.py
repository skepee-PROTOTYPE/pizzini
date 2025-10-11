"""
Upload configuration to Firestore
"""
import json
import requests

# Read local config
with open('config.json', 'r') as f:
    config = json.load(f)

# Upload to Firestore via Cloud Function
# We'll create a new function to update config
print("Configuration loaded from config.json")
print(f"Twitter enabled: {config['social_media']['twitter']['enabled']}")
print(f"API Key: {config['social_media']['twitter']['api_key']}")
print(f"Access Token: {config['social_media']['twitter']['access_token'][:20]}...")

# For now, let's use the Firebase Admin SDK approach
# But we need credentials, so let's create a cloud function instead
print("\nTo upload to Firestore, we'll create a cloud function...")
