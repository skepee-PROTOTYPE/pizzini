# Setup Weekly Token Health Check

## Why You Need This

Facebook tokens can expire, causing posting failures. This automated check runs weekly and alerts you before expiration.

## Windows Task Scheduler Setup

### Step 1: Open Task Scheduler
1. Press `Win + R`
2. Type: `taskschd.msc`
3. Press Enter

### Step 2: Create New Task
1. In the right panel, click **"Create Basic Task"**
2. Name: `Pizzini Token Monitor`
3. Description: `Weekly check for Facebook token expiration`
4. Click **Next**

### Step 3: Set Trigger
1. Select: **Weekly**
2. Click **Next**
3. Start date: Today
4. Start time: **09:00** (or your preferred time)
5. Recur every: **1 week**
6. Check: **Monday** (or your preferred day)
7. Click **Next**

### Step 4: Set Action
1. Select: **Start a program**
2. Click **Next**
3. Program/script: `C:\Users\MARCE\source\repos\Pizzini\.venv\Scripts\python.exe`
4. Add arguments: `monitor_and_alert.py`
5. Start in: `C:\Users\MARCE\source\repos\Pizzini`
6. Click **Next**

### Step 5: Finish
1. Review the settings
2. Check: **Open the Properties dialog when I click Finish**
3. Click **Finish**

### Step 6: Advanced Settings (Optional)
In the Properties dialog:
1. **General** tab:
   - Check: **Run whether user is logged on or not**
   - Check: **Run with highest privileges**

2. **Conditions** tab:
   - Uncheck: **Start the task only if the computer is on AC power**

3. **Settings** tab:
   - Check: **Run task as soon as possible after a scheduled start is missed**

4. Click **OK**

## Manual Testing

Before scheduling, test the monitor manually:

```powershell
cd C:\Users\MARCE\source\repos\Pizzini
.venv\Scripts\activate
python monitor_and_alert.py
```

You should see output like:
```
🔍 Pizzini Token Health Monitor
============================================================
✅ HEALTHY: Token expires in 45 days
```

## What Happens When Token Needs Renewal?

When the token is about to expire (< 7 days), the monitor will:

1. ✅ Create a file: `TOKEN_EXPIRATION_ALERT.txt` in your project folder
2. ✅ Log the event in: `token_health.log`
3. ✅ You'll see the alert file next time you open the project

## Responding to Alerts

When you see `TOKEN_EXPIRATION_ALERT.txt`:

1. Open terminal in project folder
2. Run: `python renew_facebook_token.py`
3. Follow the instructions
4. Delete the alert file after renewal

## Alternative: Monthly Check (Safer)

If you want more frequent checks:

In Task Scheduler:
- Trigger: **Monthly**
- Days: **1st and 15th** of each month

Or for the most safety:
- Trigger: **Weekly**
- Days: **Every Monday**

## Log File

Check `token_health.log` to see monitoring history:

```
2026-02-06 09:00:00 - HEALTHY - Token expires in 45 days
2026-02-13 09:00:00 - HEALTHY - Token expires in 38 days
2026-02-20 09:00:00 - WARNING - Token expires in 6 days
```

## Pro Tip: Never-Expiring Tokens

For business pages, you can get never-expiring tokens:

1. Ensure your Facebook App is in **Live Mode** (not Development)
2. Use a System User token (requires Business Manager)
3. Or use `extend_facebook_token.py` to get 60-day tokens

To check if you can get never-expiring tokens:
```bash
python extend_facebook_token.py
```

## Quick Reference

| Task | Command |
|------|---------|
| Check token health now | `python check_token_health.py` |
| Renew token | `python renew_facebook_token.py` |
| Extend to 60 days | `python extend_facebook_token.py` |
| Setup monitoring | Follow steps above |

## Troubleshooting

### Task doesn't run
1. Check Task Scheduler → Task History
2. Ensure Python path is correct
3. Test manually first

### No alert files created
1. Check `token_health.log` for errors
2. Verify config.json exists
3. Check file permissions

### Want email alerts?
Edit `monitor_and_alert.py` and configure SMTP settings in the `send_email_alert()` function.
