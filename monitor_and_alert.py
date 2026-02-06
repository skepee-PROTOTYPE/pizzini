#!/usr/bin/env python3
r"""
Token Monitoring and Alert System

This script should be run weekly (via Task Scheduler on Windows or cron on Linux)
to check token health and alert you before expiration.

Features:
- Checks Facebook token expiration
- Alerts if token will expire within 7 days
- Creates alert file for manual checking
- Can send email alerts (if configured)

Usage:
    python monitor_and_alert.py
    
Setup as Windows Task:
    1. Open Task Scheduler
    2. Create Basic Task
    3. Name: "Pizzini Token Monitor"
    4. Trigger: Weekly (every Monday)
    5. Action: Start a program
    6. Program: C:\Users\MARCE\source\repos\Pizzini\.venv\Scripts\python.exe
    7. Arguments: C:\Users\MARCE\source\repos\Pizzini\monitor_and_alert.py
    8. Start in: C:\Users\MARCE\source\repos\Pizzini
"""

import json
import requests
from datetime import datetime, timedelta
import os
import platform

# Try to import Windows toast notifications
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False

def check_and_alert():
    """Check token health and create alerts if needed"""
    
    log_file = "token_health.log"
    alert_file = "TOKEN_EXPIRATION_ALERT.txt"
    
    # Log this check
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        token = config['social_media']['facebook']['page_access_token']
        page_id = config['social_media']['facebook']['page_id']
        
        # Check token
        debug_url = "https://graph.facebook.com/v18.0/debug_token"
        debug_response = requests.get(debug_url, params={
            'input_token': token,
            'access_token': token
        })
        
        status = "HEALTHY"
        alert_needed = False
        message = ""
        
        if debug_response.status_code == 200:
            debug_data = debug_response.json().get('data', {})
            is_valid = debug_data.get('is_valid', False)
            expires_at = debug_data.get('expires_at', 0)
            
            if not is_valid:
                status = "INVALID"
                alert_needed = True
                message = "Token is INVALID! Posting will fail!"
                
            elif expires_at > 0:
                exp_date = datetime.fromtimestamp(expires_at)
                days_left = (exp_date - datetime.now()).days
                
                if days_left < 1:
                    status = "CRITICAL"
                    alert_needed = True
                    message = f"Token expires in {days_left} days! URGENT!"
                elif days_left < 7:
                    status = "WARNING"
                    alert_needed = True
                    message = f"Token expires in {days_left} days"
                else:
                    status = "HEALTHY"
                    message = f"Token expires in {days_left} days"
            else:
                status = "HEALTHY"
                message = "Token never expires"
        else:
            status = "ERROR"
            alert_needed = True
            message = "Could not check token status"
        
        # Write to log
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"{timestamp} - {status} - {message}\n")
        
        # Create/remove alert file
        if alert_needed:
            alert_content = f"""
╔════════════════════════════════════════════════════════════════╗
║                  🚨 FACEBOOK TOKEN ALERT 🚨                    ║
╚════════════════════════════════════════════════════════════════╝

Status: {status}
Time: {timestamp}
Message: {message}

ACTION REQUIRED:
---------------
Your Facebook Page Access Token needs attention!

To renew the token:

1. Open a terminal in: C:\\Users\\MARCE\\source\\repos\\Pizzini

2. Activate environment:
   .venv\\Scripts\\activate

3. Run renewal script:
   python renew_facebook_token.py

4. Follow the instructions to get a new token from:
   https://developers.facebook.com/tools/explorer/

5. The script will automatically update config and sync to Firebase

═══════════════════════════════════════════════════════════════

This alert was created by: monitor_and_alert.py
Check log file: {log_file}

DELETE THIS FILE AFTER RENEWING THE TOKEN
"""
            
            with open(alert_file, 'w', encoding='utf-8') as f:
                f.write(alert_content)
            
            print(f"⚠️  {status}: {message}")
            print(f"📄 Alert created: {alert_file}")
            
            # Show Windows notification
            show_windows_notification(status, message)
            
        else:
            # Remove alert file if it exists
            if os.path.exists(alert_file):
                os.remove(alert_file)
            
            print(f"✅ {status}: {message}")
        
        # Optional: Send email alert (configure SMTP settings)
        if alert_needed and status in ["CRITICAL", "INVALID"]:
            try:
                send_email_alert(status, message)
            except:
                pass  # Email not configured, skip            
            try:
                send_messenger_alert(status, message, config)
            except:
                pass  # Messenger not configured, skip        
        return not alert_needed
        
    except Exception as e:
        error_msg = f"Error during monitoring: {e}"
        with open(log_file, 'a') as f:
            f.write(f"{timestamp} - ERROR - {error_msg}\n")
        print(f"❌ {error_msg}")
        return False

def show_windows_notification(status, message):
    """Show Windows 10/11 desktop notification"""
    if platform.system() != 'Windows':
        return
    
    # Use PowerShell for reliable Windows notifications
    try:
        ps_script = f"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = 'Pizzini Social Media Automation'

$template = @"
<toast>
    <visual>
        <binding template="ToastText02">
            <text id="1">🚨 Pizzini Token Alert: $status</text>
            <text id="2">$message - Run: python renew_facebook_token.py</text>
        </binding>
    </visual>
    <actions>
        <action content="OK" arguments="dismiss" />
    </actions>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
"""
        # Write script to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ps1', delete=False) as f:
            f.write(ps_script)
            script_path = f.name
        
        import subprocess
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-File', script_path],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        # Clean up
        try:
            os.unlink(script_path)
        except:
            pass
        
        if result.returncode == 0:
            print("📢 Windows desktop notification sent!")
        else:
            print(f"⚠️  Notification warning: {result.stderr}")
            # Fallback to simple message box
            show_message_box(status, message)
            
    except Exception as e:
        print(f"⚠️  Could not show notification: {e}")
        # Final fallback
        show_message_box(status, message)

def show_message_box(status, message):
    """Fallback: Show message box (blocks until user clicks OK)"""
    try:
        import subprocess
        ps_cmd = f'[System.Windows.Forms.MessageBox]::Show("{message}`n`nRun: python renew_facebook_token.py", "Pizzini Token Alert: {status}", "OK", "Warning")'
        subprocess.run(
            ['powershell', '-Command', f'Add-Type -AssemblyName System.Windows.Forms; {ps_cmd}'],
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        print("📢 Alert message box shown!")
    except Exception as e:
        print(f"⚠️  Could not show message box: {e}")

def send_messenger_alert(status, message, config):
    """Send Facebook Messenger alert"""
    try:
        notifications_config = config.get('notifications', {})
        messenger_config = notifications_config.get('facebook_messenger', {})
        
        if not messenger_config.get('enabled', False):
            return
        
        recipient_psid = messenger_config.get('recipient_psid')
        if not recipient_psid:
            return
        
        token = config['social_media']['facebook']['page_access_token']
        
        alert_message = f"""🚨 PIZZINI TOKEN ALERT

Status: {status}
Message: {message}

⚠️ ACTION REQUIRED:
Your Facebook Page Access Token needs renewal!

To renew:
1. Open: https://developers.facebook.com/tools/explorer/
2. Get a new Page Access Token
3. Run: python renew_facebook_token.py

Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
        
        send_url = "https://graph.facebook.com/v18.0/me/messages"
        message_data = {
            'recipient': {'id': recipient_psid},
            'message': {'text': alert_message},
            'access_token': token
        }
        
        response = requests.post(send_url, json=message_data)
        
        if response.status_code == 200:
            print("📱 Facebook Messenger alert sent!")
        else:
            print(f"⚠️  Messenger alert failed: {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Could not send Messenger alert: {e}")

def send_email_alert(status, message):
    """Send email alert (optional - configure your SMTP settings)"""
    # Uncomment and configure if you want email alerts
    
    # import smtplib
    # from email.mime.text import MIMEText
    
    # smtp_server = "smtp.gmail.com"
    # smtp_port = 587
    # sender_email = "your-email@gmail.com"
    # sender_password = "your-app-password"
    # recipient_email = "your-email@gmail.com"
    
    # subject = f"🚨 Pizzini Token Alert: {status}"
    # body = f"""
    # Facebook Token Status: {status}
    # Message: {message}
    # 
    # Action Required: Renew your Facebook Page Access Token
    # 
    # Run: python renew_facebook_token.py
    # """
    
    # msg = MIMEText(body)
    # msg['Subject'] = subject
    # msg['From'] = sender_email
    # msg['To'] = recipient_email
    
    # with smtplib.SMTP(smtp_server, smtp_port) as server:
    #     server.starttls()
    #     server.login(sender_email, sender_password)
    #     server.send_message(msg)
    
    pass

if __name__ == "__main__":
    print("🔍 Pizzini Token Health Monitor")
    print("=" * 60)
    check_and_alert()
