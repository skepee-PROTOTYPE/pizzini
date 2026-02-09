# Social Media & Audio Integration Usage Guide

This guide explains how to use the new Facebook posting and audio generation features.

## New Features

### 1. **Facebook Page Posting** ✅
Post text and images to your Facebook Page using the Graph API.

### 2. **Audio Generation with Voice Selection** 🎙️
Generate high-quality audio files from your pizzini content using Google Text-to-Speech with multiple Italian voice options.

### 3. **Spotify Podcast Integration** 🎧
**Automatically upload** podcast episodes to Spotify via Anchor/Spotify for Podcasters.

---

## Setup Instructions

### 1. Install New Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `facebook-sdk` - For Facebook API integration
- `gTTS` - Google Text-to-Speech for audio generation
- `pydub` - Audio file processing
- `anchor-podcasts` - **Automatic upload** to Anchor/Spotify for Podcasters

**Note**: For `pydub` to work properly, you also need to install **ffmpeg**:
- **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use: `choco install ffmpeg`
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### 2. Get Facebook Page Access Token

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create an app (or use existing one)
3. Add "Pages" product to your app
4. Generate a **Page Access Token** (not User Token!)
5. Get your **Page ID** from your Facebook Page settings

**Important**: Generate a **long-lived** Page Access Token (60 days or permanent).

### 3. Setup Spotify for Podcasters (Anchor)

1. **Create your podcast show** (required before uploading episodes)
3. Note your login credentials (email + password)

**Note**: Episodes will be **automatically uploaded** to your Anchor podcast using the `anchor-podcasts` library.
- Implement the Anchor API for automated uploads (requires additional setup)

---

## Available Voice Options

The audio generator supports multiple Italian voices:

| Voice Key | Description | Accent |
|-----------|-------------|--------|
| `it-female` | Italian Female (Italy) | Standard Italian (Default) |
| `it-male` | Italian Male | Alternative Standard |
| `it-com.au` | Italian | Australian accent |
| `it-co.uk` | Italian | UK accent |
| `it-us` | Italian | US accent |

---

## Code Examples

### Example 1: Basic Setup with All Platforms

```python
from social_media_poster import SocialMediaManager

# Initialize manager with preferred voice
manager = SocialMediaManager(audio_voice='it-female')

# Setup X (Twitter)
manager.setup_x(
    api_key="your_x_api_key",
    api_secret="your_x_api_secret",
    access_token="your_x_access_token",
    access_token_secret="your_x_access_token_secret"
)

# Setup Instagram
manager.setup_instagram(
    username="your_instagram_username",
    password="your_instagram_password"
)

# Setup Facebook Page
manager.setup_facebook(
    page_access_token="your_long_lived_page_access_token",
    page_id="your_facebook_page_id"
)

# Setup Spotify Podcast (via Anchor)
manager.setup_spotify_podcast(
    anchor_email="your_anchor_email",
    anchor_password="your_anchor_password"
)
```

### Example 2: Post to All Platforms (with Audio)

```python
# Post content to all platforms including audio generation
results = manager.post_to_all_platforms(
    title="AIUTO PER IL PIZZINO (1°)",
    content="La parola rapporto dice che una cosa c'entra con un'altra...",
    date="17.09.2012",
    include_image=True,      # Generate and post images
    include_audio=True       # Generate audio for podcast
)

# Check results
for result in results:
    if result['success']:
        print(f"✅ {result['platform']}: Posted successfully")
    else:
        print(f"❌ {result['platform']}: {result.get('error', 'Failed')}")
```

### Example 3: Generate Audio Only (Different Voices)

```python
from social_media_poster import AudioGenerator

# List available voices
voices = AudioGenerator.list_available_voices()
for voice in voices:
    print(f"{voice['key']}: {voice['description']}")

# Create audio with female voice
audio_gen_female = AudioGenerator(voice='it-female')
audio_path_1 = audio_gen_female.create_podcast_episode(
    title="Pizzino sulla Saggezza",
    content="Il vero saggio è colui che sa di non sapere...",
    date="09.02.2026"
)
print(f"Female voice audio: {audio_path_1['audio_path']}")
print(f"Duration: {audio_path_1['duration']} seconds")

# Create audio with male voice
audio_gen_male = AudioGenerator(voice='it-male')
audio_path_2 = audio_gen_male.text_to_speech(
    text="Benvenuti al nostro pizzino quotidiano",
    title="intro"
)
print(f"Male voice audio: {audio_path_2}")

# Change voice dynamically
manager.change_audio_voice('it-us')
```

### Example 4: Facebook Only Posting

```python
from social_media_poster import FacebookPoster

# Initialize Facebook poster
fb_poster = FacebookPoster(
    page_access_token="your_page_access_token",
    page_id="your_page_id"
)

# Post text only
result = fb_poster.post_text(
    text="Nuovo pizzino oggi! 🇮🇹✨",
    link="https://your-website.com"
)

# Post with image
result = fb_poster.post_photo(
    image_path="path/to/your/image.png",
    caption="Il nostro pensiero del giorno #pizzini #saggezza"
)
```

### Example 5: Generate Images for Manual Posting

```python
from social_media_poster import ImageGenerator

image_gen = ImageGenerator(width=1080, height=1080)

# Create quote image
image_path = image_gen.create_quote_image(
    title="PENSIERO DEL GIORNO",
    content="La saggezza è sapere cosa fare, l'abilità è sapere come farlo...",
    date="09.02.2026",
    save_path="outputs/daily_quote.png"
)

print(f"Image saved to: {image_path}")
```

---

## Integration with XML Parser

Update your main script to include audio generation:

```python
from xml_parser import PizziniParser
from social_media_poster import SocialMediaManager

# Parse XML
parser = PizziniParser('pizzinifile.xml')
daily_pizzino = parser.get_pizzini_for_date('2026-02-09')

if daily_pizzino:
    # Setup manager
    manager = SocialMediaManager(audio_voice='it-female')
    
    # Configure platforms (load from config.json)
    # ... setup code here ...
    
    # Post to all platforms with audio
    results = manager.post_to_all_platforms(
        title=daily_pizzino['title'],
        content=daily_pizzino['body'],
        date=daily_pizzino['date'],
        include_image=True,
        include_audio=True  # NEW: Generate audio
    )
```

---

## Output Files

### Audio Files
Generated audio files are saved in `audio_output/` directory:
- Format: `{title}_{timestamp}.mp3`
- Also creates: `{title}_{timestamp}_metadata.json` (for Spotify uploads)

### Image Files
Temporary images are created during posting and automatically cleaned up.

---

## Facebook Page Token Guide

### Get Long-Lived Token

```bash
# Use Facebook Graph API Explorer
# 1. Get short-lived token (expires in 1 hour)
# 2. Exchange it for long-lived token using:

curl -G \
  -d "grant_type=fb_exchange_token" \
  -d "client_id={your-app-id}" \
  -d "client_secret={your-app-secret}" \
  -d "fb_exchange_token={short-lived-token}" \
  https://graph.facebook.com/v18.0/oauth/access_token
```

Add to your `config.json`:

```json
{
  "facebook": {
    "page_access_token": "YOUR_LONG_LIVED_TOKEN",
    "page_id": "YOUR_PAGE_ID"
  }
}
```

---

## Troubleshooting

### Audio Generation Issues

**Error: "ffmpeg not found"**
- Install ffmpeg (see setup instructions above)
- Make sure ffmpeg is in your system PATH

**Audio quality issues**
- Try different voice options
- Adjust `slow=True` in gTTS for clearer pronunciation

### Facebook Posting Issues  

**Error: "Invalid OAuth access token"**
- Generate a new long-lived token
- Make sure you're using a **Page** token, not a User token

**Error: "Permissions error"**
- Add required permissions in Facebook App: `pages_manage_posts`, `pages_read_engagement`

### Spotify/Anchor Issues

**Error: "anchor-podcasts not installed"**
- Run: `pip install anchor-podcasts`
- Restart your Python environment

**Error: "Failed to login to Anchor"**
- Check your Anchor credentials (email/password)
- Make sure you have created a podcast show in Anchor first
- Try logging in manually at anchor.fm to verify credentials

**Episodes not appearing**
- Check if `publish=True` in the upload_episode call
- Log into Anchor dashboard to check draft episodes
- Audio files are saved in `audio_output/` for reference

---

## Next Steps

1. **Update config.json** with your credentials
2. **Test each platform** individually before posting to all
3. **Schedule automated posts** using the scheduler module
4. **Monitor API usage** to stay within rate limits

---

## Voice Selection Best Practices

- Use `it-female` (default) for most content - natural and clear
- Use `it-male` for variety or different content types
- Test different voices to find the best fit for your audience
- Consider using different voices for different types of pizzini

---

## API Rate Limits

| Platform | Rate Limit | Notes |
|----------|-----------|-------|
| X/Twitter | 50 posts/day | For application auth |
| Instagram | ~25-30 posts/day | Account-dependent |
| Facebook Page | 200 posts/day | Per page |
| Anchor/Spotify | No official limit | Avoid spam, quality over quantity |

---

For more information, see the main [README.md](README.md) and [DEPLOYMENT_COMPLETE.md](DEPLOYMENT_COMPLETE.md).
