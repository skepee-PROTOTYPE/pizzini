# Facebook Token Renewal Reminder

## ⚠️ IMPORTANT: Renew Facebook Token Before December 5, 2025

Your Facebook Page Access Token will expire approximately **60 days** from October 6, 2025.

**Expiration Date: ~December 5, 2025**

---

## Token Renewal Steps

### 1. Generate New Token
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer)
2. Select App: **Pizzini** (ID: 3076532592551035)
3. Click **"Get Page Access Token"** (NOT User Token!)
4. Select your page: **Pizzini** (ID: 854816874372210)
5. Ensure permissions: `pages_manage_posts`, `pages_read_engagement`, `pages_show_list`
6. Copy the generated token

### 2. Extend Token to 60 Days
1. Go to [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken)
2. Paste the token from step 1
3. Click **"Debug"**
4. Click **"Extend Access Token"** button
5. Copy the **extended token**

### 3. Update Configuration
1. Open `config.json`
2. Replace the `page_access_token` value with the new extended token
3. Save the file

### 4. Upload to Firebase
Run this command in PowerShell:
```powershell
$json = Get-Content config.json -Raw
Invoke-WebRequest -Uri "https://us-central1-pizzini-91da9.cloudfunctions.net/update_config" -Method POST -Body $json -ContentType "application/json"
```

### 5. Test the New Token
```powershell
# Test locally
python test_facebook.py

# Test on Firebase
Invoke-WebRequest -Uri "https://manual-post-iw2xx6amsa-uc.a.run.app" -UseBasicParsing
```

---

## Quick Reference
- **Current Token Issued:** October 6, 2025
- **Estimated Expiration:** December 5, 2025
- **Page ID:** 854816874372210
- **App ID:** 3076532592551035
- **App Name:** Pizzini

---

## Set Your Own Reminder
Choose one of these methods:

### Option 1: Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task
3. Set trigger for **December 1, 2025** (a few days before expiration)
4. Action: Display a message "Renew Facebook Token for Pizzini!"

### Option 2: Calendar Reminder
- **Google Calendar / Outlook:** Set event for December 1, 2025
- **Title:** "Renew Facebook Token - Pizzini Bot"
- **Description:** Link to this file

### Option 3: Email Reminder
Use a service like [FollowUpThen](https://www.followupthen.com/):
- Send email to: december1@followupthen.com
- Subject: Renew Facebook Token for Pizzini

---

## Troubleshooting
If token expires before renewal:
1. Posts will fail with "Invalid OAuth access token" error
2. Check Firebase logs at https://console.firebase.google.com/project/pizzini-91da9/functions/logs
3. Follow renewal steps above to restore service
4. Posts will resume automatically on next scheduled run (6:00 AM Italy time)

---

**Last Updated:** October 6, 2025
