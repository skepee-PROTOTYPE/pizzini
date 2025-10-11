"""Test Facebook API posting"""
import requests
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

facebook_config = config['social_media']['facebook']

print("Testing Facebook API posting...")
print(f"Page ID: {facebook_config['page_id']}")
print(f"Token: {facebook_config['page_access_token'][:20]}...")
print()

try:
    # Test message
    test_message = "Test post from Pizzini automation - verificando il sistema Facebook! 🧪"
    
    # Facebook Graph API endpoint
    page_id = facebook_config['page_id']
    access_token = facebook_config['page_access_token']
    
    url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
    payload = {
        'message': test_message,
        'access_token': access_token
    }
    
    print(f"Attempting to post: '{test_message}'")
    print()
    
    response = requests.post(url, data=payload)
    response.raise_for_status()
    
    result = response.json()
    
    print("✓ SUCCESS! Post created on Facebook!")
    print(f"  Post ID: {result.get('id')}")
    print(f"  Check your Facebook Page to see the post!")
    
except requests.exceptions.HTTPError as e:
    print(f"✗ HTTP Error: {e}")
    print(f"  Response: {e.response.text}")
    print()
    print("Possible causes:")
    print("  1. Page Access Token is invalid or expired")
    print("  2. Page ID is incorrect")
    print("  3. Missing required permissions (pages_manage_posts)")
    print("  4. Token doesn't have access to this specific page")
    
except Exception as e:
    print(f"✗ Error: {type(e).__name__}")
    print(f"  Message: {e}")
