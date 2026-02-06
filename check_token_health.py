#!/usr/bin/env python3
"""
Check Facebook Token Health and Expiration

This script checks if your Facebook token is:
- Valid
- Still has posting permissions
- About to expire (warns if < 7 days)

Run this regularly to catch token issues before they cause posting failures.

Usage:
    python check_token_health.py
"""

import json
import requests
from datetime import datetime, timedelta

def check_token_health():
    """Check the health of the Facebook token"""
    
    print("=" * 70)
    print("🏥 FACEBOOK TOKEN HEALTH CHECK")
    print("=" * 70)
    print()
    
    # Load config
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Could not load config.json: {e}")
        return False
    
    token = config['social_media']['facebook']['page_access_token']
    page_id = config['social_media']['facebook']['page_id']
    
    print(f"📄 Page ID: {page_id}")
    print(f"📄 Token: {token[:50]}...")
    print()
    
    # Test 1: Basic validity
    print("🧪 Test 1: Token Validity")
    try:
        test_url = f"https://graph.facebook.com/v18.0/{page_id}"
        test_response = requests.get(test_url, params={'access_token': token})
        
        if test_response.status_code == 200:
            page_data = test_response.json()
            print(f"   ✅ Token is VALID")
            print(f"   📱 Page: {page_data.get('name', 'Unknown')}")
        else:
            error_data = test_response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            error_code = error_data.get('error', {}).get('code', 'Unknown')
            print(f"   ❌ Token is INVALID!")
            print(f"   Error ({error_code}): {error_msg}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error checking validity: {e}")
        return False
    
    print()
    
    # Test 2: Expiration check
    print("🧪 Test 2: Token Expiration")
    try:
        debug_url = "https://graph.facebook.com/v18.0/debug_token"
        debug_response = requests.get(debug_url, params={
            'input_token': token,
            'access_token': token
        })
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json().get('data', {})
            expires_at = debug_data.get('expires_at', 0)
            
            if expires_at == 0:
                print("   ✅ Token NEVER EXPIRES 🎉")
                days_left = 999999
            else:
                exp_date = datetime.fromtimestamp(expires_at)
                days_left = (exp_date - datetime.now()).days
                hours_left = (exp_date - datetime.now()).seconds // 3600
                
                print(f"   📅 Expires: {exp_date.strftime('%Y-%m-%d %H:%M')}")
                print(f"   ⏰ Time left: {days_left} days, {hours_left} hours")
                
                if days_left < 1:
                    print("   🚨 CRITICAL: Token expires in less than 24 hours!")
                    print("   Action: Run 'python renew_facebook_token.py' NOW!")
                elif days_left < 7:
                    print("   ⚠️  WARNING: Token expires soon!")
                    print("   Action: Run 'python renew_facebook_token.py' this week")
                elif days_left < 14:
                    print("   ⚡ Token expires in 2 weeks")
                    print("   Action: Consider renewing soon")
                else:
                    print("   ✅ Token has plenty of time left")
        else:
            print("   ⚠️  Could not check expiration")
            days_left = None
            
    except Exception as e:
        print(f"   ⚠️  Error checking expiration: {e}")
        days_left = None
    
    print()
    
    # Test 3: Posting permission
    print("🧪 Test 3: Posting Permission")
    try:
        test_post_url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
        test_payload = {
            'message': f'[Health Check] Token validation - {datetime.now().isoformat()}',
            'access_token': token,
            'published': False  # Create as draft, don't publish
        }
        
        post_response = requests.post(test_post_url, data=test_payload)
        
        if post_response.status_code == 200:
            print("   ✅ Token has POSTING permission")
            # Delete the draft post
            post_id = post_response.json().get('id')
            if post_id:
                delete_url = f"https://graph.facebook.com/v18.0/{post_id}"
                requests.delete(delete_url, params={'access_token': token})
        else:
            error_data = post_response.json()
            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
            print(f"   ❌ Token CANNOT post!")
            print(f"   Error: {error_msg}")
            return False
            
    except Exception as e:
        print(f"   ⚠️  Could not test posting: {e}")
    
    print()
    print("=" * 70)
    
    # Overall health status
    if days_left is not None:
        if days_left < 1:
            print("🚨 HEALTH STATUS: CRITICAL - Renew token NOW!")
            print()
            print("Run immediately: python renew_facebook_token.py")
            return False
        elif days_left < 7:
            print("⚠️  HEALTH STATUS: WARNING - Token expires soon")
            print()
            print("Recommended: python renew_facebook_token.py")
            return True
        else:
            print("✅ HEALTH STATUS: HEALTHY")
            print()
            print("Everything looks good! 🎉")
            return True
    else:
        print("✅ HEALTH STATUS: HEALTHY (assuming no expiration)")
        return True

if __name__ == "__main__":
    check_token_health()
