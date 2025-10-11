"""Debug Facebook token permissions"""
import requests
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

facebook_config = config['social_media']['facebook']
access_token = facebook_config['page_access_token']

print("Debugging Facebook Access Token...")
print()

# Check token info
url = f"https://graph.facebook.com/debug_token"
params = {
    'input_token': access_token,
    'access_token': access_token
}

response = requests.get(url, params=params)
print("Token Debug Info:")
print(json.dumps(response.json(), indent=2))
print()

# Check permissions
url2 = f"https://graph.facebook.com/me/permissions"
params2 = {
    'access_token': access_token
}

response2 = requests.get(url2, params=params2)
print("Token Permissions:")
print(json.dumps(response2.json(), indent=2))
