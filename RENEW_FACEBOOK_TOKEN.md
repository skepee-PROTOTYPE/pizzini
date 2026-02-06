# Facebook Token Renewal Guide

## Why You Need This
Your Facebook Page Access Token has expired (error 190). This happens when:
- Password is changed
- Facebook invalidates for security reasons
- Token naturally expires (60 days default)

## Step-by-Step Token Renewal

### Step 1: Go to Graph API Explorer
1. Open: https://developers.facebook.com/tools/explorer/
2. Make sure you're logged into Facebook

### Step 2: Select Your App
1. In the top right, find the dropdown that says "Facebook App"
2. Select your **Pizzini app** (or the app you created)

### Step 3: Get User Access Token
1. Click **"Get Token"** dropdown button
2. Select **"Get User Access Token"**
3. In the permissions dialog, make sure these are checked:
   - ✅ `pages_show_list`
   - ✅ `pages_read_engagement`
   - ✅ `pages_manage_posts`
4. Click **"Generate Access Token"**
5. Approve the permissions if prompted

### Step 4: Get Page Access Token
1. After getting the User Access Token, the token field will be filled
2. Click **"Get Token"** dropdown again
3. Select **"Get Page Access Token"**
4. Select your page: **"Costruiamo la Scuola"** (ID: 854816874372210)
5. The token field will update with a longer token

### Step 5: Copy the Token
1. Click the token field (it's the long string)
2. Copy the entire token (it starts with "EAA...")
3. **IMPORTANT:** This is your Page Access Token!

### Step 6: Test the Token (RECOMMENDED)
1. In Graph API Explorer, with your new token:
2. In the field next to "Submit", enter: `me/accounts`
3. Click **Submit**
4. Verify your page appears in the response

### Step 7: Update config.json
1. Open `config.json`
2. Find line ~12: `"page_access_token"`
3. Replace the old token with your new token
4. Save the file

### Step 8: Test Locally
Run in terminal:
```bash
python renew_facebook_token.py
```

This will:
- Test your new token
- Show token expiration info
- Update config.json automatically
- Sync to Firebase

### Step 9: Sync to Firebase
If you didn't use the script above, manually sync:
```bash
python sync_config_to_firebase.py
```

## Optional: Get Long-Lived Token (60 days)

The token from Graph Explorer expires quickly. For a longer-lasting token:

1. Go to: https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your Page Access Token
3. Check the expiration date
4. If it says "Expires: In about 2 months" - you're good!
5. If it says "Expires: In 1 hour" - you need to extend it

To extend:
```bash
python extend_facebook_token.py
```

## Troubleshooting

### "Token is invalid"
- Make sure you got the **Page Access Token**, not User Access Token
- Verify you selected the correct page

### "Permission denied"
- Go back to Step 3 and ensure `pages_manage_posts` is checked
- Try generating the token again

### "Page not found"
- Verify you're an admin of the Facebook Page
- Check the page ID is correct: 854816874372210

## Quick Reference

- **Your Page ID:** 854816874372210
- **Your Page:** Costruiamo la Scuola
- **Required Permission:** pages_manage_posts
- **Token Type Needed:** Page Access Token (not User Access Token)

## After Token Renewal

The system will automatically:
- ✅ Post daily at 6:00 AM Rome time
- ✅ Use the new token from Firestore
- ✅ Continue rotating through content

No need to redeploy Firebase Functions - just update the config!
