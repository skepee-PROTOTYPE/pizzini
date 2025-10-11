"""Test Twitter API authentication"""
import tweepy
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

twitter_config = config['social_media']['twitter']

print("Testing Twitter API authentication...")
print(f"API Key: {twitter_config['api_key'][:10]}...")
print(f"Access Token: {twitter_config['access_token'][:20]}...")

try:
    # Create Twitter client
    client = tweepy.Client(
        consumer_key=twitter_config['api_key'],
        consumer_secret=twitter_config['api_secret'],
        access_token=twitter_config['access_token'],
        access_token_secret=twitter_config['access_token_secret']
    )
    
    # Try to get authenticated user info
    print("\nAttempting to authenticate...")
    me = client.get_me()
    
    if me.data:
        print(f"✓ Authentication successful!")
        print(f"  Username: @{me.data.username}")
        print(f"  Name: {me.data.name}")
        print(f"  ID: {me.data.id}")
    else:
        print("✗ Authentication failed - no user data returned")
        
except tweepy.Unauthorized as e:
    print(f"\n✗ Authentication failed: Unauthorized (401)")
    print(f"  Error: {str(e)}")
    print("\nPossible reasons:")
    print("  1. API credentials are incorrect")
    print("  2. App permissions not set correctly")
    print("  3. Access tokens were regenerated but app wasn't re-authorized")
    print("\nTo fix:")
    print("  1. Go to https://developer.x.com/en/portal/dashboard")
    print("  2. Select your app")
    print("  3. Go to 'Keys and tokens' tab")
    print("  4. Under 'Authentication Tokens', click 'Regenerate' for both Access Token and Secret")
    print("  5. Run: python main.py --setup")
    print("  6. Enter the new credentials")
    
except tweepy.Forbidden as e:
    print(f"\n✗ Authentication failed: Forbidden (403)")
    print(f"  Error: {str(e)}")
    print("\nPossible reasons:")
    print("  1. App doesn't have required permissions")
    print("  2. OAuth 1.0a not enabled")
    
except Exception as e:
    print(f"\n✗ Error: {type(e).__name__}")
    print(f"  Message: {str(e)}")
