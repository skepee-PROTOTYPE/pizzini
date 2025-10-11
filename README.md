# Pizzini Social Media Automation

This project automates posting Italian philosophical content from XML files to social media platforms like X (Twitter) and Instagram.

## Features

- 📖 Parse XML content with Italian philosophical thoughts
- 🐦 Post to X (Twitter) with proper character limits
- 📸 Post to Instagram with generated quote images
- ⏰ Automated scheduling (recurring or random)
- 🎨 Automatic content formatting for each platform
- 🔐 Secure credential management
- 🇮🇹 Italian-specific hashtags and formatting
- 📊 Status monitoring and logging

## Installation

1. **Clone or download this project to your computer**

2. **Install Python dependencies:**
```bash
pip install tweepy instagrapi Pillow schedule cryptography requests
```

3. **Copy the configuration template:**
```bash
copy config_template.json config.json
```

## Quick Start

### 1. Interactive Setup
Run the setup wizard to configure your social media accounts:
```bash
python main.py --setup
```

This will guide you through:
- Connecting to X (Twitter) API
- Setting up Instagram credentials
- Configuring posting schedule
- Setting content preferences

### 2. Test Your Setup
Test posting without actually publishing:
```bash
python main.py --test
```

### 3. Start Automation
Begin automated posting:
```bash
python main.py --start
```

## Configuration

### Social Media Platforms

#### X (Twitter) Setup
1. Go to [Twitter Developer Portal](https://developer.twitter.com/)
2. Create an app and get your API keys
3. Add them to your `config.json`:
```json
{
  "social_media": {
    "twitter": {
      "enabled": true,
      "api_key": "your_api_key",
      "api_secret": "your_api_secret", 
      "access_token": "your_access_token",
      "access_token_secret": "your_access_token_secret"
    }
  }
}
```

#### Instagram Setup
Add your Instagram credentials:
```json
{
  "social_media": {
    "instagram": {
      "enabled": true,
      "username": "your_username",
      "password": "your_password"
    }
  }
}
```

### Scheduling Options

#### Recurring Posts
Post every X days at a specific time:
```json
{
  "scheduling": {
    "mode": "recurring",
    "recurring_settings": {
      "interval_days": 7,
      "start_time": "09:00"
    }
  }
}
```

#### Random Posts
Post X times per week at random times:
```json
{
  "scheduling": {
    "mode": "random", 
    "random_settings": {
      "posts_per_week": 3,
      "time_windows": [
        ["09:00", "12:00"],
        ["15:00", "18:00"]
      ]
    }
  }
}
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

## Platform-Specific Formatting

### X (Twitter)
- Maximum 280 characters
- Automatically truncates long content
- Adds 2-3 relevant hashtags
- Smart text breaking at sentence boundaries

### Instagram  
- Generates quote images automatically
- Full content with Italian hashtags
- Professional quote formatting
- Date attribution

## File Structure

```
Pizzini/
├── main.py                 # Main automation script
├── xml_parser.py          # XML content parser
├── social_media_poster.py # Platform posting logic
├── content_formatter.py   # Content formatting for each platform
├── scheduler.py           # Automated scheduling system
├── config_manager.py      # Configuration management
├── config_template.json   # Configuration template
├── pizzinifile.xml        # Your content source
└── pizzini_automation.log # Activity log
```

## Security

- Credentials stored in `config.json` (keep this file private)
- Optional encryption for sensitive data
- Secure password handling for Instagram
- API tokens never logged

## Troubleshooting

### Common Issues

1. **"Module not found" errors:**
   ```bash
   pip install tweepy instagrapi Pillow schedule cryptography
   ```

2. **Twitter API errors:**
   - Check your API keys are correct
   - Ensure your Twitter app has read/write permissions
   - Verify your account is not suspended

3. **Instagram login issues:**
   - Instagram may require 2FA verification
   - Try logging in manually first
   - Check username/password are correct

4. **No posts being scheduled:**
   - Check `python main.py --status`
   - Verify scheduling is enabled in config
   - Ensure entry IDs exist in XML

### Logs
Check `pizzini_automation.log` for detailed error information.

## Advanced Usage

### Custom Hashtags
Modify `content_formatter.py` to add your own hashtag categories:
```python
ITALIAN_HASHTAGS = [
    '#your_custom_hashtag',
    '#saggezza', 
    '#filosofia'
]
```

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