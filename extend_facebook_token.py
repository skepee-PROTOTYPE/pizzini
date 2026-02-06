#!/usr/bin/env python3
"""
Extend Facebook Page Access Token to Long-Lived Token

This script converts your short-lived Page Access Token (1-2 hours)
to a long-lived token (60 days).

Usage:
    python extend_facebook_token.py
"""

import json
import requests
from datetime import datetime

print("=" * 70)
print("🔄 FACEBOOK TOKEN EXTENSION - GET LONG-LIVED TOKEN (60 DAYS)")
print("=" * 70)
print()

# Load current config
with open('config.json', 'r') as f:
    config = json.load(f)

current_token = config['social_media']['facebook']['page_access_token']
page_id = config['social_media']['facebook']['page_id']

# You'll need these from your Facebook App
# Go to: https://developers.facebook.com/apps/
# Select your app → Settings → Basic
print("📋 To extend your token, you need your App credentials:")
print("   Go to: https://developers.facebook.com/apps/")
print("   Select 'Pizzini' app → Settings → Basic")
print()

app_id = input("Enter your App ID: ").strip()
app_secret = input("Enter your App Secret: ").strip()

if not app_id or not app_secret:
    print("❌ App ID and Secret are required!")
    exit(1)

print()
print("🔍 Checking current token expiration...")

try:
    # Check current token status
    debug_url = "https://graph.facebook.com/v18.0/debug_token"
    debug_response = requests.get(debug_url, params={
        'input_token': current_token,
        'access_token': current_token
    })
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json().get('data', {})
        expires_at = debug_data.get('expires_at', 0)
        is_valid = debug_data.get('is_valid', False)
        
        if not is_valid:
            print("❌ Current token is invalid!")
            print("   Please get a new token first: python renew_facebook_token.py")
            exit(1)
        
        if expires_at == 0:
            print("✅ Current token already never expires!")
            print("   No need to extend.")
            exit(0)
        else:
            exp_date = datetime.fromtimestamp(expires_at)
            days_left = (exp_date - datetime.now()).days
            print(f"⏰ Current token expires: {exp_date.strftime('%Y-%m-%d %H:%M')} ({days_left} days)")
    
except Exception as e:
    print(f"⚠️  Could not check current token: {e}")

print()
print("🔄 Extending token to long-lived (60 days)...")

try:
    # First, exchange for long-lived user access token
    exchange_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    exchange_params = {
        'grant_type': 'fb_exchange_token',
        'client_id': app_id,
        'client_secret': app_secret,
        'fb_exchange_token': current_token
    }
    
    exchange_response = requests.get(exchange_url, params=exchange_params)
    
    if exchange_response.status_code != 200:
        error_data = exchange_response.json()
        print(f"❌ Failed to extend token!")
        print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        print()
        print("Common issues:")
        print("  1. Invalid App ID or App Secret")
        print("  2. Token is already long-lived")
        print("  3. App doesn't have proper permissions")
        exit(1)
    
    exchange_data = exchange_response.json()
    long_lived_token = exchange_data.get('access_token')
    
    if not long_lived_token:
        print("❌ No access token received!")
        exit(1)
    
    print("✅ Long-lived user token obtained!")
    
    # Now get the long-lived page access token
    accounts_url = f"https://graph.facebook.com/v18.0/me/accounts"
    accounts_response = requests.get(accounts_url, params={
        'access_token': long_lived_token
    })
    
    if accounts_response.status_code != 200:
        print("❌ Could not get page tokens!")
        exit(1)
    
    accounts_data = accounts_response.json()
    pages = accounts_data.get('data', [])
    
    # Find our page
    page_token = None
    for page in pages:
        if page['id'] == page_id:
            page_token = page['access_token']
            print(f"✅ Long-lived page token obtained for: {page['name']}")
            break
    
    if not page_token:
        print(f"❌ Could not find page with ID: {page_id}")
        print(f"   Available pages: {[p['name'] for p in pages]}")
        exit(1)
    
    # Verify the new token
    debug_response = requests.get(debug_url, params={
        'input_token': page_token,
        'access_token': page_token
    })
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json().get('data', {})
        expires_at = debug_data.get('expires_at', 0)
        
        if expires_at == 0:
            print("   ⏰ New token: NEVER EXPIRES! 🎉")
        else:
            exp_date = datetime.fromtimestamp(expires_at)
            days_left = (exp_date - datetime.now()).days
            print(f"   ⏰ New token expires: {exp_date.strftime('%Y-%m-%d %H:%M')} ({days_left} days)")
    
    # Update config
    print()
    print("💾 Updating config.json...")
    
    config['social_media']['facebook']['page_access_token'] = page_token
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ config.json updated!")
    
    # Sync to Firebase
    print()
    print("☁️  Syncing to Firebase...")
    
    try:
        project_id = "pizzini-91da9"
        function_url = f"https://us-central1-{project_id}.cloudfunctions.net/update_config"
        
        response = requests.post(function_url, json=config, headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("✅ Configuration synced to Firebase!")
        else:
            print(f"⚠️  Firebase sync failed. Run manually: python sync_config_to_firebase.py")
            
    except Exception as e:
        print(f"⚠️  Firebase sync failed. Run manually: python sync_config_to_firebase.py")
    
    print()
    print("=" * 70)
    print("✨ TOKEN EXTENDED SUCCESSFULLY!")
    print("=" * 70)
    print()
    print("Your token is now long-lived and will last 60 days.")
    print("Set a reminder to renew it before expiration!")
    print()
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
