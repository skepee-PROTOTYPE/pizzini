# Facebook API Setup Guide

## Prerequisites
1. A Facebook account
2. A Facebook Page (where you want to post the pizzini content)

## Step 1: Create a Facebook Page (if you don't have one)

1. Go to https://www.facebook.com/pages/create
2. Choose "Business or Brand"
3. Name your page (e.g., "Pizzini - Pensieri Filosofici")
4. Category: "Art" or "Education" or "Writer"
5. Complete the setup

## Step 2: Create a Facebook App

1. Go to https://developers.facebook.com/
2. Click **"My Apps"** in the top right
3. Click **"Create App"**
4. Choose **"Business"** as app type
5. Fill in:
   - **App Name**: "Pizzini Automation" (or any name)
   - **App Contact Email**: Your email
6. Click **"Create App"**

## Step 3: Add Pages API

1. In your new app dashboard, scroll down to **"Add Products"**
2. Find **"Facebook Login"** and click **"Set Up"**
3. Skip the quickstart (click **"Settings"** in left menu under Facebook Login)
4. No configuration needed here for now

## Step 4: Get Page Access Token

### Option A: Using Graph API Explorer (Easiest for Testing)

1. Go to https://developers.facebook.com/tools/explorer/
2. In the top right, select your app from the dropdown
3. Click **"Generate Access Token"**
4. Grant permissions:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
5. Click **"Generate Access Token"** and authorize
6. You'll see a short-lived token - **DO NOT USE THIS YET**

7. To get a long-lived token:
   - Click the **"i"** (info) icon next to the access token
   - Click **"Open in Access Token Tool"**
   - Click **"Extend Access Token"**
   - This gives you a 60-day token

8. To get a Page Access Token (never expires):
   - In Graph API Explorer, make this GET request:
     ```
     /me/accounts
     ```
   - Click **"Submit"**
   - You'll see a list of your Pages
   - Find your Pizzini page and copy its `access_token`
   - This Page Access Token never expires!

### Option B: Using Access Token Debugger (For Long-Lived Token)

1. Go to https://developers.facebook.com/tools/debug/accesstoken/
2. Paste your user access token
3. Click **"Debug"**
4. Click **"Extend Access Token"**
5. Use the extended token to get Page token as described above

## Step 5: Get Your Page ID

**Method 1: From Graph API Explorer**
- When you made the `/me/accounts` request, you saw your page's `id`

**Method 2: From your Page**
1. Go to your Facebook Page
2. Click **"About"** in the left menu
3. Scroll down to find **"Page ID"** or **"Page transparency"**
4. Copy the numeric ID

**Method 3: Quick way**
1. Go to https://developers.facebook.com/tools/explorer/
2. Make a GET request to: `/me/accounts`
3. Your Page ID and access token are both in the response

## Step 6: Test Your Credentials

Before adding to config, test them:

1. Go to https://developers.facebook.com/tools/explorer/
2. Paste your **Page Access Token** in the Access Token field
3. Change the request to POST
4. Use this endpoint: `/{your-page-id}/feed`
5. Add parameters:
   ```json
   {
     "message": "Test post from Pizzini automation!"
   }
   ```
6. Click **"Submit"**
7. If it works, check your Facebook Page - you should see the post!

## Step 7: Add to Configuration

Now run:
```powershell
python main.py --setup
```

When prompted for Facebook:
- **Page Access Token**: Paste the long-lived Page Access Token
- **Page ID**: Paste your Page ID (numeric)

## Important Notes

### Token Expiration
- **Page Access Tokens** from apps you own never expire (as long as the app is active)
- If you change your Facebook password, you'll need to regenerate tokens
- If your app goes into development mode restrictions, tokens may stop working

### Permissions Required
Your app needs these permissions:
- `pages_show_list` - To see your pages
- `pages_read_engagement` - To read page data
- `pages_manage_posts` - To create posts

### App Review (For Public Use)
- For testing with your own page: **NOT NEEDED**
- For posting to other people's pages: You'll need Facebook App Review
- Since you're posting to your own page, you can skip app review!

### Testing

After setup, test with:
```powershell
# Test local posting
python -c "import requests; print(requests.post('https://graph.facebook.com/v18.0/YOUR_PAGE_ID/feed', data={'message': 'Test!', 'access_token': 'YOUR_TOKEN'}).json())"
```

## Troubleshooting

**Error: "Invalid OAuth access token"**
- Token expired or incorrect - regenerate

**Error: "Insufficient permissions"**
- Need to add required permissions in Graph API Explorer

**Error: "Application does not have permission"**
- App needs to be added as a Page admin
- Go to Page Settings > Page Roles > Add your app

**Can't find /me/accounts**
- Make sure you're logged into Facebook
- Token needs `pages_show_list` permission

## Quick Reference

- **Developer Console**: https://developers.facebook.com/apps/
- **Graph API Explorer**: https://developers.facebook.com/tools/explorer/
- **Access Token Tool**: https://developers.facebook.com/tools/debug/accesstoken/
- **Page Settings**: https://www.facebook.com/pages/?category=your_pages

## What You Need for Config

```json
{
  "social_media": {
    "facebook": {
      "enabled": true,
      "page_access_token": "YOUR_LONG_PAGE_ACCESS_TOKEN_HERE",
      "page_id": "YOUR_PAGE_ID_HERE"
    }
  }
}
```
