# Facebook Page + Spotify Podcast Setup

## What This Does

When you run the posting system, for each pizzino it will:

1. **📘 Post to Facebook Page**
   - Posts an image with the pizzino text
   - Includes title, content, and date
   - Automatically formatted for Facebook

2. **🎙️ Generate Audio File**
   - Converts the pizzino text to Italian audio (MP3)
   - You can choose the voice (5 Italian options available)
   - Saves to `audio_output/` folder

3. **🎧 Publish to Spotify Podcast**
   - **Automatically uploads** the audio to your Anchor/Spotify podcast
   - Creates the episode with title and description
   - Publishes it live to Spotify

---

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

Also install **ffmpeg**:
- Windows: `choco install ffmpeg` or download from [ffmpeg.org](https://ffmpeg.org)

### Step 2: Create Your Anchor Podcast

1. Go to [anchor.fm](https://anchor.fm)
2. Sign up / Log in
3. **Create a new podcast show**
   - Add podcast name (e.g., "Pizzini Quotidiani")
   - Add description
   - Upload cover art (1400x1400 to 3000x3000 pixels)
   - Complete the setup
4. Save your login credentials

### Step 3: Add Credentials to config.json

```json
{
  "social_media": {
    "facebook": {
      "enabled": true,
      "page_access_token": "YOUR_FACEBOOK_PAGE_TOKEN",
      "page_id": "YOUR_PAGE_ID"
    }
  },
  "podcast": {
    "enabled": true,
    "platform": "anchor",
    "anchor_email": "your_anchor_email@example.com",
    "anchor_password": "your_anchor_password",
    "auto_upload": true
  },
  "posting_settings": {
    "include_audio": true,
    "audio_settings": {
      "voice": "it-female"
    }
  }
}
```

---

## How to Get Facebook Page Access Token

### Step-by-Step:

1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Create an App (or use existing)
3. Add "Pages" product to your app
4. Go to **Graph API Explorer**
5. Select your app, select your page
6. Add permissions: `pages_manage_posts`, `pages_read_engagement`
7. Generate Token → Copy the Page Access Token
8. Get your Page ID from your Facebook Page settings

**Important**: Generate a **long-lived token** (60 days or permanent)

---

## Usage Example

```python
from social_media_poster import SocialMediaManager
import json

# Load config
with open('config.json') as f:
    config = json.load(f)

# Initialize manager
manager = SocialMediaManager(audio_voice='it-female')

# Setup Facebook
manager.setup_facebook(
    page_access_token=config['social_media']['facebook']['page_access_token'],
    page_id=config['social_media']['facebook']['page_id']
)

# Setup Spotify Podcast
manager.setup_spotify_podcast(
    anchor_email=config['podcast']['anchor_email'],
    anchor_password=config['podcast']['anchor_password']
)

# Post a pizzino to both Facebook and Spotify
results = manager.post_to_all_platforms(
    title="PENSIERO DEL GIORNO",
    content="La saggezza è sapere cosa fare, l'abilità è sapere come farlo.",
    date="09.02.2026",
    include_image=True,   # Creates image for Facebook
    include_audio=True    # Creates and uploads audio to Spotify
)

# Check results
for result in results:
    print(f"{result['platform']}: {'✅ Success' if result['success'] else '❌ Failed'}")
```

---

## What Gets Created

### Facebook Post:
- ✅ Image with pizzino text
- ✅ Caption with title and content
- ✅ Hashtags (configured per platform)
- ✅ Posted to your Facebook Page

### Spotify Podcast Episode:
- ✅ MP3 audio file (Italian voice)
- ✅ Episode title from pizzino title
- ✅ Episode description from pizzino content
- ✅ **Automatically published** to Spotify/Anchor
- ✅ Appears in your podcast feed

### Files Saved:
- `audio_output/{title}_{timestamp}.mp3` - The audio file
- `audio_output/{title}_{timestamp}_metadata.json` - Episode metadata

---

## Available Italian Voices

| Voice | Description |
|-------|-------------|
| `it-female` | Italian Female (Default, recommended) |
| `it-male` | Italian Male |
| `it-com.au` | Italian (Australian accent) |
| `it-co.uk` | Italian (UK accent) |
| `it-us` | Italian (US accent) |

Change voice in config.json or:
```python
manager.change_audio_voice('it-male')
```

---

## Testing Before Publishing

Run the test script to verify everything works:

```bash
python test_new_features.py
```

This will test:
- ✅ Audio generation
- ✅ Image generation  
- ✅ Facebook setup
- ✅ File creation

---

## Troubleshooting

**"anchor-podcasts not installed"**
```bash
pip install anchor-podcasts
```

**"Failed to login to Anchor"**
- Check email/password in config.json
- Make sure you created a podcast show in Anchor first
- Try logging in manually at anchor.fm

**"ffmpeg not found"**
- Install ffmpeg on your system
- Add to PATH environment variable
- Restart terminal/IDE

**Facebook token expired**
- Generate a new long-lived Page Access Token
- Update config.json

---

## Summary

✅ **Facebook**: Automatic posting with images
✅ **Spotify**: Automatic audio upload to podcast  
✅ **Voice Selection**: 5 Italian voice options
✅ **One Command**: Posts to both platforms simultaneously

Your pizzini will now reach your audience on **Facebook** (visual) and **Spotify** (audio)!
