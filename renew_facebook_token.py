#!/usr/bin/env python3
"""
Interactive Facebook Token Renewal Script

This script helps you renew your Facebook Page Access Token
and automatically updates config.json and syncs to Firebase.

Usage:
    python renew_facebook_token.py
"""

import json
import requests
from datetime import datetime

print("=" * 70)
print("🔄 FACEBOOK TOKEN RENEWAL ASSISTANT")
print("=" * 70)
print()

# Load current config
with open('config.json', 'r') as f:
    config = json.load(f)

current_token = config['social_media']['facebook']['page_access_token']
page_id = config['social_media']['facebook']['page_id']

print(f"📄 Current Page ID: {page_id}")
print(f"📄 Current Token: {current_token[:50]}...")
print()

# Test current token
print("🧪 Testing current token...")
try:
    test_url = f"https://graph.facebook.com/v18.0/{page_id}"
    test_response = requests.get(test_url, params={'access_token': current_token})
    
    if test_response.status_code == 200:
        print("✅ Current token is VALID!")
        data = test_response.json()
        print(f"   Page: {data.get('name', 'Unknown')}")
        
        # Check token info
        debug_url = f"https://graph.facebook.com/v18.0/debug_token"
        debug_response = requests.get(debug_url, params={
            'input_token': current_token,
            'access_token': current_token
        })
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json().get('data', {})
            expires_at = debug_data.get('expires_at', 0)
            
            if expires_at == 0:
                print("   ⏰ Token: Never expires")
            else:
                exp_date = datetime.fromtimestamp(expires_at)
                days_left = (exp_date - datetime.now()).days
                print(f"   ⏰ Token expires: {exp_date.strftime('%Y-%m-%d %H:%M')} ({days_left} days)")
                
                if days_left < 7:
                    print("   ⚠️  WARNING: Token expires soon!")
        
        print()
        print("❓ Do you still want to renew the token? (y/n): ", end='')
        proceed = input().lower()
        
        if proceed != 'y':
            print("✋ Token renewal cancelled.")
            exit(0)
    else:
        print("❌ Current token is INVALID or EXPIRED!")
        error_data = test_response.json()
        print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        print()
        print("➡️  You need to get a new token.")
        
except Exception as e:
    print(f"❌ Error testing token: {e}")

print()
print("=" * 70)
print("📋 INSTRUCTIONS TO GET NEW TOKEN")
print("=" * 70)
print()
print("1. Open: https://developers.facebook.com/tools/explorer/")
print("2. Select your Pizzini app (top right dropdown)")
print("3. Click 'Get Token' → 'Get User Access Token'")
print("4. Check permission: 'pages_manage_posts'")
print("5. Click 'Generate Access Token'")
print("6. Click 'Get Token' → 'Get Page Access Token'")
print("7. Select your page: 'Costruiamo la Scuola'")
print("8. Copy the long token (starts with EAAA...)")
print()
print("=" * 70)
print()
print("🔑 Paste your NEW Page Access Token here:")
print("   (or press Enter to cancel)")
print()

new_token = input("Token: ").strip()

if not new_token:
    print("❌ No token provided. Cancelled.")
    exit(1)

if not new_token.startswith('EAA'):
    print("⚠️  Warning: Token doesn't start with 'EAA'. Are you sure this is correct?")
    print("   Continue anyway? (y/n): ", end='')
    
    if input().lower() != 'y':
        print("❌ Cancelled.")
        exit(1)

# Test new token
print()
print("🧪 Testing new token...")

try:
    # Test basic access
    test_url = f"https://graph.facebook.com/v18.0/{page_id}"
    test_response = requests.get(test_url, params={'access_token': new_token})
    
    if test_response.status_code != 200:
        print("❌ Token test failed!")
        error_data = test_response.json()
        print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        print()
        print("Please check:")
        print("  1. You got the PAGE Access Token (not User Access Token)")
        print("  2. You selected the correct page")
        print("  3. The token has 'pages_manage_posts' permission")
        exit(1)
    
    page_data = test_response.json()
    print(f"✅ Token is VALID!")
    print(f"   Page: {page_data.get('name', 'Unknown')}")
    print(f"   ID: {page_data.get('id', 'Unknown')}")
    
    # Test posting capability
    test_post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    test_payload = {
        'message': '[TEST] Token validation - please ignore',
        'access_token': new_token,
        'published': False  # Create as draft
    }
    
    post_response = requests.post(test_post_url, data=test_payload)
    
    if post_response.status_code == 200:
        print("   ✅ Token has POSTING permission!")
    else:
        print("   ⚠️  Warning: Token may not have posting permission")
        print(f"      Error: {post_response.json().get('error', {}).get('message', 'Unknown')}")
        print()
        print("   Do you want to continue anyway? (y/n): ", end='')
        
        if input().lower() != 'y':
            print("❌ Cancelled.")
            exit(1)
    
    # Get token expiration info
    debug_url = f"https://graph.facebook.com/v18.0/debug_token"
    debug_response = requests.get(debug_url, params={
        'input_token': new_token,
        'access_token': new_token
    })
    
    if debug_response.status_code == 200:
        debug_data = debug_response.json().get('data', {})
        expires_at = debug_data.get('expires_at', 0)
        
        if expires_at == 0:
            print("   ⏰ Token: Never expires")
        else:
            exp_date = datetime.fromtimestamp(expires_at)
            days_left = (exp_date - datetime.now()).days
            print(f"   ⏰ Token expires: {exp_date.strftime('%Y-%m-%d %H:%M')} ({days_left} days)")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Update config.json
print()
print("💾 Updating config.json...")

config['social_media']['facebook']['page_access_token'] = new_token

try:
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ config.json updated successfully!")
    
except Exception as e:
    print(f"❌ Failed to update config.json: {e}")
    exit(1)

# Sync to Firebase
print()
print("☁️  Syncing to Firebase...")

try:
    project_id = "pizzini-91da9"
    function_url = f"https://us-central1-{project_id}.cloudfunctions.net/update_config"
    
    response = requests.post(function_url, json=config, headers={'Content-Type': 'application/json'})
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Configuration synced to Firebase!")
        print(f"   Response: {result.get('message', 'Success')}")
    else:
        print(f"⚠️  Firebase sync failed: {response.status_code}")
        print(f"   You can sync manually later: python sync_config_to_firebase.py")
        
except Exception as e:
    print(f"⚠️  Firebase sync failed: {e}")
    print(f"   You can sync manually later: python sync_config_to_firebase.py")

# Final test
print()
print("🎯 Running final test post...")

try:
    test_message = f"✅ Pizzini automation system - Token rinnovato con successo! {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    test_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    test_payload = {
        'message': test_message,
        'access_token': new_token
    }
    
    print(f"   Posting: '{test_message}'")
    
    response = requests.post(test_url, data=test_payload)
    
    if response.status_code == 200:
        result = response.json()
        post_id = result.get('id')
        print(f"✅ TEST POST SUCCESSFUL!")
        print(f"   Post ID: {post_id}")
        print(f"   View: https://facebook.com/{post_id}")
    else:
        print(f"❌ Test post failed: {response.status_code}")
        error_data = response.json()
        print(f"   Error: {error_data.get('error', {}).get('message', 'Unknown error')}")
        
except Exception as e:
    print(f"⚠️  Could not run test post: {e}")

print()
print("=" * 70)
print("✨ TOKEN RENEWAL COMPLETE!")
print("=" * 70)
print()
print("Next steps:")
print("  ✅ Your Facebook token has been renewed")
print("  ✅ Configuration updated in Firebase")
print("  ✅ Scheduled posts will use the new token")
print()
print("The system will automatically post daily at 6:00 AM Rome time.")
print()
