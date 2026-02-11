"""
Firebase Cloud Functions for Pizzini Social Media Automation - Phase 1
"""

from firebase_functions import https_fn
import json
from datetime import datetime

# Initialize Firebase Admin
import firebase_admin
from firebase_admin import firestore

if not firebase_admin._apps:
    firebase_admin.initialize_app()

@https_fn.on_request()
def hello_world(req):
    """Simple test function"""
    return {
        "message": "Hello from Pizzini automation!",
        "timestamp": datetime.now().isoformat(),
        "status": "success"
    }

@https_fn.on_request()
def update_config(req):
    """Update configuration in Firestore from request body"""
    try:
        # Get JSON data from request
        request_json = req.get_json(silent=True)
        
        if not request_json:
            return {"status": "error", "message": "No JSON data provided"}
        
        # Update configuration in Firestore
        db = firestore.client()
        config_ref = db.collection('config').document('social_media')
        config_ref.set(request_json)
        
        return {
            "status": "success",
            "message": "Configuration updated successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@https_fn.on_request()
def test_config(req):
    """Test Firestore connection"""
    try:
        db = firestore.client()
        config_ref = db.collection('config').document('social_media')
        config_doc = config_ref.get()
        
        if config_doc.exists:
            config = config_doc.to_dict()
            return {
                "status": "success", 
                "config_exists": True,
                "config": config,  # Return the full config for debugging
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "status": "success",
                "config_exists": False,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@https_fn.on_request()
def upload_xml_test(req):
    """Upload XML content from request body or use test content"""
    try:
        from firebase_admin import storage
        
        # Check if request has XML content
        xml_content = req.get_data(as_text=True)
        
        if not xml_content or len(xml_content) < 100:
            # Use test XML content if no content provided
            xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
    <channel>
        <title>Pizzini Test</title>
        <description>Test content for Pizzini automation</description>
        <item>
            <title>Test Entry 1</title>
            <description>Questo è un test per verificare che il sistema funzioni correttamente.</description>
            <author>Sistema Test</author>
            <date>2025-10-04</date>
        </item>
        <item>
            <title>Test Entry 2</title>
            <description>Un altro test per assicurarsi che tutto funzioni.</description>
            <author>Sistema Test</author>
            <date>2025-10-04</date>
        </item>
    </channel>
</rss>'''
        
        # Upload to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        blob.upload_from_string(xml_content, content_type='application/xml')
        
        return {
            "status": "success",
            "message": f"XML uploaded successfully ({len(xml_content)} bytes)",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@https_fn.on_request()
def test_xml_load(req):
    """Test function to load and parse XML from storage"""
    try:
        from firebase_admin import storage
        import xml.etree.ElementTree as ET
        
        # Load XML from Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        
        if not blob.exists():
            return {"status": "error", "message": "XML file not found in storage"}
        
        xml_content = blob.download_as_text()
        
        # Parse XML - handle the real pizzini structure
        root = ET.fromstring(xml_content)
        entries = []
        
        # The real structure uses <pizzini> elements with Title and Content
        for item in root.findall('.//{http://www.w3.org/2001/XMLSchema}pizzini'):
            # Skip schema definition elements
            continue
            
        # Look for pizzini elements without namespace
        for item in root.findall('.//pizzini'):
            title = item.find('Title')
            content = item.find('Content')
            date = item.find('Date')
            id_elem = item.find('Id')
            
            # Skip if this is the root element
            if title is None and content is None:
                continue
            
            entries.append({
                "id": id_elem.text if id_elem is not None else "",
                "title": title.text if title is not None else "No title",
                "content": content.text if content is not None else "No content",
                "date": date.text if date is not None else ""
            })
        
        return {
            "status": "success",
            "entries_found": len(entries),
            "sample_entries": entries[:3] if entries else [],  # Show first 3
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@https_fn.on_request()
def manual_post(req):
    """HTTP function for manual posting to social media"""
    try:
        from firebase_admin import storage
        import xml.etree.ElementTree as ET
        import random
        
        # Load configuration from Firestore
        db = firestore.client()
        config_ref = db.collection('config').document('social_media')
        config_doc = config_ref.get()
        
        if not config_doc.exists:
            return {"status": "error", "message": "Configuration not found"}
        
        config = config_doc.to_dict()
        
        # Load XML content from Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        
        if not blob.exists():
            return {"status": "error", "message": "XML file not found in storage"}
        
        xml_content = blob.download_as_text()
        
        # Parse XML to get entries
        root = ET.fromstring(xml_content)
        entries = []
        
        for item in root.findall('.//pizzini'):
            title = item.find('Title')
            content = item.find('Content')
            date = item.find('Date')
            id_elem = item.find('Id')
            
            # Skip if this is the root or schema element
            if title is None and content is None:
                continue
            
            entries.append({
                "id": id_elem.text if id_elem is not None else "",
                "title": title.text if title is not None else "",
                "content": content.text if content is not None else "",
                "date": date.text if date is not None else ""
            })
        
        if not entries:
            return {"status": "error", "message": "No entries found in XML"}
        
        # Select a random entry
        entry = random.choice(entries)
        
        # Format full content for Facebook (no length limit)
        full_content = f'"{entry["content"]}"'
        if entry["title"]:
            full_content = f'{entry["title"]}\n\n{full_content}'
        
        # Format shortened content for Twitter (280 char limit)
        twitter_max_length = 250
        twitter_content = full_content
        if len(twitter_content) > twitter_max_length:
            twitter_content = twitter_content[:twitter_max_length-3] + "..."
        
        # Add Italian hashtags
        hashtags = "\n\n#filosofia #pensieri #saggezza #citazioni"
        tweet_text = twitter_content + hashtags
        facebook_text = full_content + hashtags
        
        # Post to social media platforms
        platforms_posted = []
        twitter_post_id = None
        facebook_post_id = None
        post_errors = []
        
        # Post to Twitter if enabled
        twitter_config = config.get('social_media', {}).get('twitter', {})
        if twitter_config.get('enabled', False):
            try:
                import tweepy
                
                # Setup Twitter client with explicit OAuth 1.0a
                auth = tweepy.OAuth1UserHandler(
                    consumer_key=twitter_config['api_key'],
                    consumer_secret=twitter_config['api_secret'],
                    access_token=twitter_config['access_token'],
                    access_token_secret=twitter_config['access_token_secret']
                )
                
                client = tweepy.Client(
                    consumer_key=twitter_config['api_key'],
                    consumer_secret=twitter_config['api_secret'],
                    access_token=twitter_config['access_token'],
                    access_token_secret=twitter_config['access_token_secret'],
                    wait_on_rate_limit=True
                )
                
                # Post tweet
                response = client.create_tweet(text=tweet_text)
                twitter_post_id = response.data['id']
                platforms_posted.append("twitter")
                
            except Exception as e:
                error_msg = f"Twitter: {type(e).__name__} - {str(e)}"
                post_errors.append(error_msg)
        
        # Post to Facebook if enabled
        facebook_config = config.get('social_media', {}).get('facebook', {})
        if facebook_config.get('enabled', False):
            try:
                import requests
                
                # Facebook Graph API endpoint
                page_id = facebook_config['page_id']
                access_token = facebook_config['page_access_token']
                
                # Use full text for Facebook (no length limit)
                fb_message = facebook_text
                
                # Post to Facebook Page
                url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
                payload = {
                    'message': fb_message,
                    'access_token': access_token
                }
                
                response = requests.post(url, data=payload)
                response.raise_for_status()
                
                result = response.json()
                facebook_post_id = result.get('id')
                platforms_posted.append("facebook")
                
            except Exception as e:
                error_msg = f"Facebook: {type(e).__name__} - {str(e)}"
                post_errors.append(error_msg)
        
        # Return error if all platforms failed
        if not platforms_posted:
            return {
                "status": "error",
                "message": f"Failed to post to all platforms. Errors: {'; '.join(post_errors)}",
                "entry_id": entry["id"],
                "entry_title": entry["title"]
            }
        
        # Log posting activity to Firestore
        activity_ref = db.collection('posting_activity').document()
        activity_ref.set({
            'timestamp': datetime.now(),
            'entry_id': entry["id"],
            'entry_title': entry["title"],
            'entry_content': entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
            'platforms': platforms_posted,
            'twitter_post_id': twitter_post_id,
            'facebook_post_id': facebook_post_id,
            'errors': post_errors if post_errors else None,
            'success': len(platforms_posted) > 0
        })
        
        result = {
            "status": "success" if platforms_posted else "partial",
            "message": "Post created successfully" if platforms_posted else "Some platforms failed",
            "entry_id": entry["id"],
            "entry_title": entry["title"],
            "content_preview": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
            "platforms": platforms_posted,
            "timestamp": datetime.now().isoformat()
        }
        
        if twitter_post_id:
            result["twitter_post_id"] = twitter_post_id
        if facebook_post_id:
            result["facebook_post_id"] = facebook_post_id
        if post_errors:
            result["errors"] = post_errors
        
        return result
        
    except Exception as e:
        return {"status": "error", "message": f"Posting failed: {str(e)}"}

@https_fn.on_request()
def get_status(req):
    """Get system status"""
    try:
        db = firestore.client()
        
        # Check config
        config_ref = db.collection('config').document('social_media')
        config_doc = config_ref.get()
        config = config_doc.to_dict() if config_doc.exists else {}
        
        # Get recent activity
        recent_activity = []
        try:
            activity_ref = db.collection('posting_activity').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(5)
            for doc in activity_ref.stream():
                activity_data = doc.to_dict()
                if 'timestamp' in activity_data:
                    activity_data['timestamp'] = activity_data['timestamp'].isoformat()
                recent_activity.append(activity_data)
        except Exception as e:
            pass  # No activities yet
        
        return {
            "status": "healthy",
            "config_loaded": bool(config),
            "platforms_configured": list(config.keys()) if config else [],
            "recent_activity": recent_activity,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Import scheduler for scheduled functions
from firebase_functions import scheduler_fn

@scheduler_fn.on_schedule(schedule="0 6 * * *", timezone="Europe/Rome")
def scheduled_post(event):
    """Scheduled function to post daily content at 6 AM Italy time"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("Starting scheduled post")
    
    try:
        from firebase_admin import storage
        import xml.etree.ElementTree as ET
        import random
        
        # Load configuration from Firestore
        db = firestore.client()
        config_ref = db.collection('config').document('social_media')
        config_doc = config_ref.get()
        
        if not config_doc.exists:
            logger.error("Configuration not found")
            return {"status": "error", "message": "Configuration not found"}
        
        config = config_doc.to_dict()
        
        # Check if scheduling is enabled
        if not config.get('scheduling', {}).get('enabled', False):
            logger.info("Scheduling is disabled")
            return {"status": "skipped", "message": "Scheduling disabled"}
        
        # Load XML content from Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        
        if not blob.exists():
            logger.error("XML file not found")
            return {"status": "error", "message": "XML file not found in storage"}
        
        xml_content = blob.download_as_text()
        
        # Parse XML to get entries
        root = ET.fromstring(xml_content)
        entries = []
        
        for item in root.findall('.//pizzini'):
            title = item.find('Title')
            content = item.find('Content')
            date = item.find('Date')
            id_elem = item.find('Id')
            
            # Skip if this is the root or schema element
            if title is None and content is None:
                continue
            
            entries.append({
                "id": id_elem.text if id_elem is not None else "",
                "title": title.text if title is not None else "",
                "content": content.text if content is not None else "",
                "date": date.text if date is not None else ""
            })
        
        if not entries:
            logger.error("No entries found")
            return {"status": "error", "message": "No entries found in XML"}
        
        # Select a random entry
        entry = random.choice(entries)
        logger.info(f"Selected entry ID: {entry['id']}, Title: {entry['title']}")
        
        # Format full content for Facebook (no length limit)
        full_content = f'"{entry["content"]}"'
        if entry["title"]:
            full_content = f'{entry["title"]}\n\n{full_content}'
        
        # Format shortened content for Twitter (280 char limit)
        twitter_max_length = 250
        twitter_content = full_content
        if len(twitter_content) > twitter_max_length:
            twitter_content = twitter_content[:twitter_max_length-3] + "..."
        
        # Add Italian hashtags
        hashtags = "\n\n#filosofia #pensieri #saggezza #citazioni"
        tweet_text = twitter_content + hashtags
        facebook_text = full_content + hashtags
        
        # Post to social media platforms
        platforms_posted = []
        twitter_post_id = None
        facebook_post_id = None
        post_errors = []
        
        # Post to Twitter if enabled
        twitter_config = config.get('social_media', {}).get('twitter', {})
        if twitter_config.get('enabled', False):
            try:
                import tweepy
                
                # Setup Twitter client with explicit OAuth 1.0a
                auth = tweepy.OAuth1UserHandler(
                    consumer_key=twitter_config['api_key'],
                    consumer_secret=twitter_config['api_secret'],
                    access_token=twitter_config['access_token'],
                    access_token_secret=twitter_config['access_token_secret']
                )
                
                client = tweepy.Client(
                    consumer_key=twitter_config['api_key'],
                    consumer_secret=twitter_config['api_secret'],
                    access_token=twitter_config['access_token'],
                    access_token_secret=twitter_config['access_token_secret'],
                    wait_on_rate_limit=True
                )
                
                # Post tweet
                response = client.create_tweet(text=tweet_text)
                twitter_post_id = response.data['id']
                platforms_posted.append("twitter")
                logger.info(f"Successfully posted to Twitter: {twitter_post_id}")
                
            except Exception as e:
                error_msg = f"Twitter: {type(e).__name__} - {str(e)}"
                post_errors.append(error_msg)
                logger.error(f"Failed to post to Twitter: {str(e)}")
        
        # Post to Facebook if enabled
        facebook_config = config.get('social_media', {}).get('facebook', {})
        if facebook_config.get('enabled', False):
            try:
                import requests
                
                # Facebook Graph API endpoint
                page_id = facebook_config['page_id']
                access_token = facebook_config['page_access_token']
                
                # Use full text for Facebook (no length limit)
                fb_message = facebook_text
                
                # Post to Facebook Page
                url = f"https://graph.facebook.com/v18.0/{page_id}/feed"
                payload = {
                    'message': fb_message,
                    'access_token': access_token
                }
                
                response = requests.post(url, data=payload)
                response.raise_for_status()
                
                result = response.json()
                facebook_post_id = result.get('id')
                platforms_posted.append("facebook")
                logger.info(f"Successfully posted to Facebook: {facebook_post_id}")
                
            except Exception as e:
                error_msg = f"Facebook: {type(e).__name__} - {str(e)}"
                post_errors.append(error_msg)
                logger.error(f"Failed to post to Facebook: {str(e)}")
        
        # Generate and upload podcast episode
        podcast_config = config.get('podcast', {})
        if podcast_config.get('enabled', False):
            try:
                import os
                from automated_podcast_publisher import AutomatedPodcastPublisher
                from content_formatter import ContentFormatter
                
                # Set Azure credentials from Firestore config
                azure_config = config.get('azure', {})
                if azure_config:
                    os.environ['AZURE_SPEECH_KEY'] = azure_config.get('speech_key', '')
                    os.environ['AZURE_SPEECH_REGION'] = azure_config.get('speech_region', '')
                
                # Generate audio
                from social_media_poster import AudioGenerator
                podcast_voice = podcast_config.get('voice', 'azure-calimero')
                audio_gen = AudioGenerator(
                    voice=podcast_voice,
                    azure_key=azure_config.get('speech_key', ''),
                    azure_region=azure_config.get('speech_region', '')
                )
                episode_data = audio_gen.create_podcast_episode(
                    title=entry["title"],
                    content=entry["content"],
                    date=entry.get("date", "")
                )
                
                audio_path = episode_data['audio_path']
                logger.info(f"Generated podcast audio: {audio_path}")
                
                # Upload to Spotify via RSS
                podcast_publisher = AutomatedPodcastPublisher()
                formatter = ContentFormatter()
                podcast_description = formatter.format_for_platform(
                    title=entry["title"],
                    content=entry["content"],
                    platform='linkedin',
                    date=entry.get("date", ""),
                    include_hashtags=False
                )['text']
                
                podcast_result = podcast_publisher.publish_episode(
                    audio_path=audio_path,
                    title=entry["title"],
                    description=podcast_description
                )
                
                if podcast_result.get('success'):
                    platforms_posted.append("spotify_podcast")
                    logger.info(f"🎙️ Podcast episode published to Spotify!")
                else:
                    error_msg = f"Podcast: {podcast_result.get('error', 'Unknown error')}"
                    post_errors.append(error_msg)
                    logger.error(f"Failed to publish podcast: {podcast_result.get('error')}")
                    
            except Exception as e:
                error_msg = f"Podcast: {type(e).__name__} - {str(e)}"
                post_errors.append(error_msg)
                logger.error(f"Failed to publish podcast: {str(e)}")
        
        # Log posting activity to Firestore
        activity_ref = db.collection('posting_activity').document()
        activity_ref.set({
            'timestamp': datetime.now(),
            'entry_id': entry["id"],
            'entry_title': entry["title"],
            'entry_content': entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
            'platforms': platforms_posted,
            'twitter_post_id': twitter_post_id,
            'facebook_post_id': facebook_post_id,
            'errors': post_errors if post_errors else None,
            'success': len(platforms_posted) > 0,
            'scheduled': True
        })
        
        logger.info(f"Scheduled post completed successfully")
        
        result = {
            "status": "success" if platforms_posted else "error",
            "message": "Scheduled post created successfully" if platforms_posted else "All platforms failed",
            "entry_id": entry["id"],
            "entry_title": entry["title"],
            "platforms": platforms_posted
        }
        
        if twitter_post_id:
            result["twitter_post_id"] = twitter_post_id
        if facebook_post_id:
            result["facebook_post_id"] = facebook_post_id
        if post_errors:
            result["errors"] = post_errors
        
        return result
        
    except Exception as e:
        logger.error(f"Scheduled post failed: {str(e)}")
        return {"status": "error", "message": f"Scheduled posting failed: {str(e)}"}