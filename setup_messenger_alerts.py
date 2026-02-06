#!/usr/bin/env python3
"""
Setup Facebook Messenger Notifications

This script helps you set up direct Facebook Messenger alerts
when your token is about to expire.

Prerequisites:
1. You must be an admin of the Facebook Page
2. You must send at least one message to the page first (to get your PSID)
3. Your app must have 'pages_messaging' permission

Usage:
    python setup_messenger_alerts.py
"""

import json
import requests

print("=" * 70)
print("📱 FACEBOOK MESSENGER ALERT SETUP")
print("=" * 70)
print()

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except Exception as e:
    print(f"❌ Could not load config.json: {e}")
    exit(1)

token = config['social_media']['facebook']['page_access_token']
page_id = config['social_media']['facebook']['page_id']

print(f"📄 Page ID: {page_id}")
print()

# Step 1: Get conversations to find user's PSID
print("🔍 Step 1: Finding your Facebook user ID (PSID)...")
print()
print("To receive messages, you need to:")
print("  1. Go to your Facebook Page: https://facebook.com/{page_id}")
print("  2. Send a message to the page (any message, like 'Hi')")
print("  3. Wait a few seconds")
print()
input("Press Enter after you've sent a message to the page...")
print()

try:
    # Get conversations
    conversations_url = f"https://graph.facebook.com/v18.0/{page_id}/conversations"
    conv_response = requests.get(conversations_url, params={
        'access_token': token,
        'fields': 'participants,messages{message,from}'
    })
    
    if conv_response.status_code != 200:
        error = conv_response.json().get('error', {})
        print(f"❌ Could not get conversations: {error.get('message', 'Unknown error')}")
        print()
        print("Possible issues:")
        print("  1. Your app needs 'pages_messaging' permission")
        print("  2. Token might not have messaging permissions")
        print()
        print("To fix:")
        print("  1. Go to: https://developers.facebook.com/tools/explorer/")
        print("  2. When getting token, also check 'pages_messaging' permission")
        print("  3. Run: python renew_facebook_token.py")
        exit(1)
    
    conversations = conv_response.json().get('data', [])
    
    if not conversations:
        print("❌ No conversations found!")
        print("   Make sure you sent a message to the page first.")
        exit(1)
    
    print(f"✅ Found {len(conversations)} conversation(s)")
    print()
    
    # Find admin's PSID
    print("👤 People who have messaged your page:")
    psids = []
    
    for conv in conversations:
        participants = conv.get('participants', {}).get('data', [])
        for participant in participants:
            psid = participant.get('id')
            name = participant.get('name', 'Unknown')
            
            if psid != page_id:  # Not the page itself
                psids.append({'id': psid, 'name': name})
                print(f"   - {name} (ID: {psid})")
    
    print()
    
    if not psids:
        print("❌ No user PSIDs found. Send a message to the page first.")
        exit(1)
    
    # Ask user to select their PSID
    if len(psids) == 1:
        selected_psid = psids[0]['id']
        print(f"✅ Using PSID: {selected_psid} ({psids[0]['name']})")
    else:
        print("Multiple users found. Enter the number for YOUR account:")
        for i, user in enumerate(psids):
            print(f"   {i+1}. {user['name']} (ID: {user['id']})")
        print()
        choice = int(input("Your choice (1-{}): ".format(len(psids))))
        selected_psid = psids[choice-1]['id']
    
    print()
    
    # Step 2: Test sending a message
    print("🧪 Step 2: Testing message sending...")
    
    test_message = "🔔 Test Alert from Pizzini Automation System!\n\nThis is how you'll receive token expiration alerts. ✅"
    
    send_url = f"https://graph.facebook.com/v18.0/me/messages"
    message_data = {
        'recipient': {'id': selected_psid},
        'message': {'text': test_message},
        'access_token': token
    }
    
    send_response = requests.post(send_url, json=message_data)
    
    if send_response.status_code == 200:
        print("✅ TEST MESSAGE SENT!")
        print("   Check your Facebook Messenger - you should have received a message!")
        print()
    else:
        error = send_response.json().get('error', {})
        print(f"❌ Failed to send message: {error.get('message', 'Unknown error')}")
        print()
        print("Common issues:")
        print("  1. App needs 'pages_messaging' permission")
        print("  2. Page messaging might be restricted")
        print("  3. You need to message the page first")
        exit(1)
    
    # Step 3: Save PSID to config
    print("💾 Step 3: Saving configuration...")
    
    if 'notifications' not in config:
        config['notifications'] = {}
    
    config['notifications']['facebook_messenger'] = {
        'enabled': True,
        'recipient_psid': selected_psid
    }
    
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Configuration saved!")
    print()
    
    print("=" * 70)
    print("✨ MESSENGER ALERTS CONFIGURED!")
    print("=" * 70)
    print()
    print("When your token is about to expire, you'll receive:")
    print("  📱 Facebook Messenger message")
    print("  🪟 Windows desktop notification")
    print("  📄 Alert file in project folder")
    print()
    print("The monitoring system will check weekly and alert you automatically.")
    print()
    print("Next: Set up weekly monitoring with Task Scheduler")
    print("See: SETUP_WEEKLY_CHECK.md")
    print()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
