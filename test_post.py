"""Test posting to Twitter with detailed error info"""
import tweepy
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

twitter_config = config['social_media']['twitter']

print("Testing Twitter posting...")
print(f"Account: @x_pizzini")
print(f"Permissions: Read and Write")
print()

try:
    # Create Twitter client
    client = tweepy.Client(
        consumer_key=twitter_config['api_key'],
        consumer_secret=twitter_config['api_secret'],
        access_token=twitter_config['access_token'],
        access_token_secret=twitter_config['access_token_secret']
    )
    
    # Try to post a simple test tweet
    test_tweet = "Test tweet from Pizzini automation - verificando il sistema 🧪"
    
    print(f"Attempting to post: '{test_tweet}'")
    print()
    
    response = client.create_tweet(text=test_tweet)
    
    print("✓ SUCCESS! Tweet posted successfully!")
    print(f"  Tweet ID: {response.data['id']}")
    print(f"  Tweet text: {response.data['text']}")
    
except tweepy.Forbidden as e:
    print(f"✗ FORBIDDEN (403) Error")
    print(f"  Full error: {e}")
    print()
    print("Possible causes:")
    print("  1. Your Twitter account might be new and has posting restrictions")
    print("  2. Your account might need phone verification")
    print("  3. Your account might be in restricted mode")
    print("  4. The app might need 'Elevated' access (not just 'Essential')")
    print()
    print("To check:")
    print("  1. Try posting manually from twitter.com to verify your account works")
    print("  2. Check if your account has phone verification enabled")
    print("  3. Check Developer Portal > Products > Your app's access level")
    
except tweepy.TweepyException as e:
    print(f"✗ Twitter API Error: {type(e).__name__}")
    print(f"  Error: {e}")
    
except Exception as e:
    print(f"✗ Unexpected Error: {type(e).__name__}")
    print(f"  Message: {e}")
