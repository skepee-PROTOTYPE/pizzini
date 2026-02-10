# Pizzini Social Media Automation

Automated daily publishing of Italian philosophical content to Facebook and podcast platforms using Firebase Cloud Functions.

## Features

- 📖 Parse XML content with Italian philosophical thoughts
- 📘 Automated daily Facebook posts to "Costruiamo la Scuola" page
- 🎙️ Text-to-speech podcast generation (gTTS)
- ☁️ Serverless deployment on Firebase Cloud Functions
- ⏰ Scheduled automation (6:00 AM Europe/Rome daily)
- 🔐 Secure credential management via Firebase RuntimeConfig
- 🇮🇹 Italian-specific content formatting
- 📊 Cloud monitoring and logging

## Architecture

- **Deployment**: Firebase Cloud Functions (Python 3.11)
- **Scheduler**: Cloud Scheduler (daily at 6:00 AM Europe/Rome)
- **Storage**: Firebase Firestore for configuration
- **TTS**: gTTS (Google Text-to-Speech) for podcast generation
- **Social**: Facebook Graph API v18.0

## Podcast Information

**I Pizzini di Don Villa**
- 🎙️ **Title**: I Pizzini di Don Villa
- 📖 **Description**: I pensieri e gli insegnamenti di Don Villa, condivisi giornalmente attraverso i suoi famosi pizzini
- 👤 **Author**: Don Villa
- 📡 **RSS Feed**: [https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml](https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml)
- 📂 **Category**: Religion & Spirituality
- 🎨 **Cover Art**: [View Cover](https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg)
- 🔊 **Audio Format**: MP3, Italian language
- ⏱️ **Frequency**: Daily episodes (6:00 AM Europe/Rome)
- 📥 **Subscribe**: Copy RSS feed URL to your podcast app (Apple Podcasts, Spotify, etc.)

## Installation

1. **Clone this repository:**
```bash
git clone https://github.com/skepee-PROTOTYPE/pizzini.git
cd pizzini
```

2. **InGet Facebook Page Access Token
1. Go to [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app and page
3. Generate a long-lived Page Access Token with `pages_manage_posts` permission
4. Add to `config.json`:
```json
{
  "social_media": {
    "facebook": {
      "enabled": true,
      "page_access_token": "your_token_here",
      "page_id": "your_page_id"
    }
  }
}
```

### 2. Deploy to Firebase
```bash
cd functions
firebase deploy --only functions
```

### 3. Test Manually
Trigger a test post via HTTP:
```bash
curl https://us-central1-YOUR_PROJECT.cloudfunctions.net/manual_post
```

### 4. Subscribe to Podcast
Add the RSS feed to your podcast app:
```
https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml
```

### 5. Monitor Scheduled Posts
Check Cloud Scheduler:
```bash
gcloud scheduler jobs list --location=us-central1
```

This will guide you through:
- Connecting to X (Twitter) API
- Setting up Instagram credentials
- Configuring posting schedule
- Setting content preferences

### 2. Test Your Setup
Test posting without actually publishing:
```bash
pythFacebook Setup
Get a long-lived Page Access Token:
1. Visit [Facebook Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app → Get User Access Token
3. Add `pages_manage_posts` permission
4. Click "Generate Access Token"
5. Exchange for long-lived token (60 days)
6. Add to `config.json`

See [FACEBOOK_SETUP_GUIDE.md](FACEBOOK_SETUP_GUIDE.md) for detailed steps.

### Azure Text-to-Speech (Optional)
For higher quality podcast audio:
1. Create Azure Speech Service
2. Get API key and region
3. Store in Firebase RuntimeConfig:
```bash
gcloud beta runtime-config configs variables set speech_key "YOUR_KEY" --config-name=azure
gcloud beta runtime-config configs variables set speech_region "YOUR_REGION" --config-name=azure
```

### Podcast Configuration
Edit podcast metadata in `config.json`:
```json
{
  "podcast_info": {
    "title": "I Pizzini di Don Villa",
    "description": "Your podcast description",
    "author": "Don Villa",
    "email": "your@email.com",
    "rss_url": "https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml",
    "category": "Religion & Spirituality",
    "cover_art": "https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg"
  }
}
```

### Scheduling
Default: Daily at 6:00 AM Europe/Rome timezone

To change schedule, edit `functions/main.py`:
```python
@scheduler_fn.on_schedule(schedule="0 6 * * *", timezone="Europe/Rome")
def scheduled_post(event: scheduler_fn.ScheduledEvent) -> None:
```

## Usage Commands

### Basic Commands
```bash
# Show all available entries
python main.py --list-entries

# Post a specific entry immediately
python main.py --post-now 1

# Check system status  
python main.py --status

# Stop automation
python main.py --stop
```

### Testing
```bash
# Test with first entry
python main.py --test

# Test with specific entry
python main.py --test 1
```

## Content Format

The system reads from `pizzinifile.xml` with this structure:
```xml
<pizzini>
  <Id>1</Id>
  <Date>17.09.2012</Date>
  <Title>AIUTO PER IL PIZZINO (1°)</Title>
  <Content>Your Italian philosophical content here...</Content>
</pizzini>
```

## Podcast Distribution

### Subscribe to Podcast

**RSS Feed URL:**
```
https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml
```

### Add to Podcast Platforms

**Apple Podcasts:**
1. Go to [Apple Podcasts Connect](https://podcastsconnect.apple.com/)
2. Submit RSS feed: `https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml`
3. Verify ownership and publish

**Spotify:**
1. Go to [Spotify for Podcasters](https://podcasters.spotify.com/)
2. Add your podcast RSS feed
3. Claim and verify

**Google Podcasts:**
- Feed is automatically indexed from RSS
- Verify at [Google Podcasts Manager](https://podcastsmanager.google.com/)

**Other Platforms:**
Most podcast apps accept RSS feeds directly:
- Pocket Casts
- Overcast
- Castro
- Podcast Addict
- And more...


### Cloud Functions Available

| Function | URL | Purpose |
|----------|-----|---------|
| `scheduled_post` | N/A (scheduler only) | Daily automated posting |
| `manual_post` | `/manual_post` | Trigger immediate post |
| `get_status` | `/get_status` | Check system status |
| `test_config` | `/test_config` | View current config |
| `update_config` | `/update_config` | Update Firestore config |

### Local Testing
```bash
# Parse XML and test content
python xml_parser.py

# Test Facebook posting
python social_media_poster.py

# Check token health
python check_token_health.py
```

### Renewing Facebook Token
Facebook Page Access Tokens expire every 60 days.

```bash
# Check token expiration
python check_token_health.py

# Get new token (manual)
py**Secrets Management**: All sensitive credentials stored in:
  - Firebase Firestore (encrypted at rest)
  - Firebase RuntimeConfig for Azure keys
  - GitHub Secrets (for CI/CD)
- **Token Protection**: Facebook tokens never committed to git
- **Configuration**: `config.json` and `serviceAccountKey.json` in `.gitignore`
- **API Security**: Cloud Functions require proper authentication
- **Token Monitoring**: Automated expiration checks and alerts.md](RENEW_FACEBOOK_TOKEN.md) for full guide. config_manager.py      # Configuration management
├── config_template.json   # Configuration template
├── pizzinifile.xml        # Your content source
└── pizzini_automation.log # Activity log
```

## Security

- Credentials stored in `config.json` (keep this file private)
- Optional encryption for sensitive data
- Secure password handling for Instagram
- API tokens never logged

## TrFacebook posts failing:**
   ```bash
   # Check token health
   python check_token_health.py
   
   # Token likely expired - renew it
   python renew_facebook_token.py
   ```

2. **Deployment errors:**
   ```bash
   # Remove venv from functions folder (causes ENOENT errors)
   rm -rf functions/venv
   
   # Deploy with fresh venv
   cd functions
   python -m venv venv
   venv\Scripts\activate
   pip install firebase-functions
   cd ..
   firebase deploy --only functions
   ```

3. **gTTS "not defined" errors:**
   - Ensure `gTTS>=2.3.0` is in `functions/requirements.txt`
   -Manual Posting
Trigger posts outside the schedule:
```bash
# Via HTTP
curl https://us-central1-YOUR_PROJECT.cloudfunctions.net/manual_post

# Via gcloud
gcloud functions call manual_post --region=us-central1
```

### Viewing Cloud Scheduler Jobs
```bash
# List all scheduler jobs
gcloud scheduler jobs list --location=us-central1

# Describe specific job
gcloud scheduler jobs describe firebase-schedule-scheduled_post-us-central1 --location=us-central1

# Trigger manually
gcloud scheduler jobs run firebase-schedule-scheduled_post-us-central1 --location=us-central1
```

### Monitoring
```bash
# View function logs
gcloud functions logs read scheduled_post --region=us-central1 --limit=50

# Monitor in real-time
gcloud functions logs read scheduled_post --region=us-central1 --follow
```

### Updating Configuration
```bash
# Sync local config to Firestore
python sync_config_to_firebase.py

# VDocumentation

- **[FACEBOOK_SETUP_GUIDE.md](FACEBOOK_SETUP_GUIDE.md)** - Complete Facebook integration guide
- **[RENEW_FACEBOOK_TOKEN.md](RENEW_FACEBOOK_TOKEN.md)** - Token renewal instructions
- **[FIREBASE_DEPLOYMENT.md](FIREBASE_DEPLOYMENT.md)** - Deployment guide
- **[FIREBASE_BILLING_GUIDE.md](FIREBASE_BILLING_GUIDE.md)** - Cost optimization tips
- **[SOCIAL_MEDIA_USAGE_GUIDE.md](SOCIAL_MEDIA_USAGE_GUIDE.md)** - Usage instructions

## Recent Updates (Feb 2026)

- ✅ Fixed Facebook token expiration handling
- ✅ Added gTTS library for podcast generation
- ✅ Disabled Twitter posting (Facebook-only)
- ✅ Deployed `scheduled_post` Cloud Function
- ✅ Removed old `daily_pizzini_automation` function
- ✅ Updated Azure Speech Services key
- ✅ Cleaned up temporary scripts and documentation

## Support

**Automated Monitoring:**
- Token health checks run weekly
- Expiration alerts sent via console logs

**Manual Checks:**
```bash
# Check system status
python check_token_health.py

# View recent logs
gcloud functions logs read --limit=20
```

## License

This project is for personal use. Ensure compliance with:
- Facebook Platform Terms of Service
- Firebase Terms of Service
- Content usage rights for pizzinifile.xml

### Multiple XML Files
To use different XML files, update `config.json`:
```json
{
  "content_settings": {
    "xml_file_path": "your_other_file.xml"
  }
}
```

### Filtering Content
Exclude specific entries:
```json
{
  "content_settings": {
    "exclude_entry_ids": [1, 3, 5]
  }
}
```

## Support

For issues or questions:
1. Check the logs in `pizzini_automation.log`
2. Run `python main.py --status` to diagnose problems
3. Use `python main.py --test` to verify setup

## License

This project is for personal use. Ensure you comply with each social media platform's terms of service and API usage policies.