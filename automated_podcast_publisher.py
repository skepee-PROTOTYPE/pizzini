"""
Automated Podcast Publishing via RSS Feed + Firebase Storage
This is the professional way to automate podcast episode publishing
"""
import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import xml.etree.ElementTree as ET
from xml.dom import minidom

logger = logging.getLogger(__name__)

class AutomatedPodcastPublisher:
    """
    Automatically publish podcast episodes by:
    1. Uploading audio to Firebase Storage (public URL)
    2. Adding episode to RSS feed
    3. Spotify/Anchor auto-detects new episodes from RSS feed
    """
    
    def __init__(self, config_path: str = 'config.json'):
        """Initialize automated podcast publisher"""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.podcast_config = self.config.get('podcast_info', {})
        self.rss_file = 'podcast_feed.xml'
        self.episodes = []
        
        # Load existing RSS feed if it exists
        if os.path.exists(self.rss_file):
            self._load_existing_feed()
        
        logger.info("Automated Podcast Publisher initialized")
    
    def _load_existing_feed(self):
        """Load existing episodes from RSS feed"""
        try:
            tree = ET.parse(self.rss_file)
            root = tree.getroot()
            channel = root.find('channel')
            
            for item in channel.findall('item'):
                episode = {
                    'title': item.find('title').text,
                    'description': item.find('description').text,
                    'audio_url': item.find('enclosure').get('url'),
                    'pub_date': item.find('pubDate').text,
                    'guid': item.find('guid').text
                }
                self.episodes.append(episode)
            
            logger.info(f"Loaded {len(self.episodes)} existing episodes from RSS feed")
        except Exception as e:
            logger.warning(f"Could not load existing feed: {e}")
    
    def upload_to_firebase(self, audio_path: str) -> Optional[str]:
        """Upload audio file to Firebase Storage and get public URL
        
        Args:
            audio_path: Local path to audio file
            
        Returns:
            Public URL of uploaded file
        """
        try:
            import firebase_admin
            from firebase_admin import credentials, storage
            
            # Initialize Firebase if not already done
            if not firebase_admin._apps:
                cred = credentials.Certificate('serviceAccountKey.json')
                
                # Get project ID from credentials
                with open('serviceAccountKey.json', 'r') as f:
                    cred_data = json.load(f)
                    project_id = cred_data.get('project_id')
                
                firebase_admin.initialize_app(cred, {
                    'storageBucket': project_id  # Use bucket name without .appspot.com
                })
            
            bucket = storage.bucket()
            
            # Enable Storage if not enabled
            logger.info("📤 Checking Firebase Storage...")
            
            # Create blob path
            filename = os.path.basename(audio_path)
            blob_path = f'podcast_audio/{filename}'
            blob = bucket.blob(blob_path)
            
            # Upload file
            logger.info(f"📤 Uploading {filename} to Firebase Storage...")
            blob.upload_from_filename(audio_path, content_type='audio/mpeg')
            
            # Make public
            blob.make_public()
            
            public_url = blob.public_url
            logger.info(f"✅ Upload complete! Public URL: {public_url}")
            
            return public_url
            
        except ImportError:
            logger.error("Firebase Admin SDK not installed. Install: pip install firebase-admin")
            return None
        except Exception as e:
            logger.warning(f"Firebase Storage upload failed: {e}")
            logger.warning("💡 Don't worry! You can still host audio files manually.")
            logger.warning("   Options:")
            logger.warning("   1. Upload to Firebase Hosting (already configured)")
            logger.warning("   2. Use any web hosting service")
            logger.warning("   3. Use SoundCloud, Archive.org, or podcast hosting")
            return None
    
    def add_episode_to_rss(self, audio_url: str, title: str, description: str,
                          pub_date: Optional[datetime] = None, duration: int = 0):
        """Add new episode to RSS feed
        
        Args:
            audio_url: Public URL to audio file
            title: Episode title
            description: Episode description
            pub_date: Publication date (defaults to now)
            duration: Duration in seconds
        """
        if pub_date is None:
            pub_date = datetime.now()
        
        episode = {
            'title': title,
            'description': description,
            'audio_url': audio_url,
            'pub_date': pub_date.strftime('%a, %d %b %Y %H:%M:%S GMT'),
            'guid': f"{self.podcast_config.get('website', '')}/episode/{pub_date.strftime('%Y%m%d%H%M%S')}",
            'duration': duration
        }
        
        self.episodes.insert(0, episode)  # Add at beginning (most recent first)
        logger.info(f"Added episode to RSS: {title}")
    
    def generate_rss_feed(self):
        """Generate complete RSS 2.0 feed with iTunes podcast tags"""
        
        # Create RSS root
        rss = ET.Element('rss', {
            'version': '2.0',
            'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
            'xmlns:content': 'http://purl.org/rss/1.0/modules/content/',
            'xmlns:atom': 'http://www.w3.org/2005/Atom'
        })
        
        channel = ET.SubElement(rss, 'channel')
        
        # Podcast metadata
        ET.SubElement(channel, 'title').text = self.podcast_config.get('title', 'I Pizzini di Don Villa')
        ET.SubElement(channel, 'description').text = self.podcast_config.get('description', 
            'I pensieri e gli insegnamenti di Don Villa, condivisi giornalmente attraverso i suoi famosi pizzini')
        ET.SubElement(channel, 'link').text = self.podcast_config.get('website', 'https://pizzini-b5c63.web.app')
        ET.SubElement(channel, 'language').text = 'it'
        ET.SubElement(channel, 'copyright').text = f'© {datetime.now().year} Don Villa'
        ET.SubElement(channel, 'itunes:author').text = self.podcast_config.get('author', 'Don Villa')
        ET.SubElement(channel, 'itunes:summary').text = self.podcast_config.get('description', '')
        ET.SubElement(channel, 'itunes:explicit').text = 'no'
        ET.SubElement(channel, 'itunes:category', {'text': 'Religion & Spirituality'})
        
        # Cover art (required by Spotify)
        cover_art_url = self.podcast_config.get('cover_art', 'https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg')
        ET.SubElement(channel, 'itunes:image', {'href': cover_art_url})
        ET.SubElement(channel, 'image').text = None  # Add image element
        img = channel.find('image')
        ET.SubElement(img, 'url').text = cover_art_url
        ET.SubElement(img, 'title').text = self.podcast_config.get('title', 'I Pizzini di Don Villa')
        ET.SubElement(img, 'link').text = self.podcast_config.get('website', 'https://pizzini-b5c63.web.app')
        
        # iTunes owner
        owner = ET.SubElement(channel, 'itunes:owner')
        ET.SubElement(owner, 'itunes:name').text = self.podcast_config.get('author', 'Don Villa')
        ET.SubElement(owner, 'itunes:email').text = self.podcast_config.get('email', 'skepee01@gmail.com')
        
        # Self-referencing RSS URL (important for podcast platforms)
        rss_url = self.podcast_config.get('rss_url', 'https://pizzini-b5c63.web.app/podcast_feed.xml')
        ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {
            'href': rss_url,
            'rel': 'self',
            'type': 'application/rss+xml'
        })
        
        # Add all episodes
        for episode in self.episodes:
            item = ET.SubElement(channel, 'item')
            ET.SubElement(item, 'title').text = episode['title']
            ET.SubElement(item, 'description').text = episode['description']
            ET.SubElement(item, 'itunes:summary').text = episode['description']
            ET.SubElement(item, 'pubDate').text = episode['pub_date']
            ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = episode['guid']
            ET.SubElement(item, 'link').text = episode['audio_url']
            
            # Audio enclosure
            ET.SubElement(item, 'enclosure', {
                'url': episode['audio_url'],
                'type': 'audio/mpeg',
                'length': '1'  # Will be updated with actual file size
            })
            
            if episode.get('duration', 0) > 0:
                ET.SubElement(item, 'itunes:duration').text = str(episode['duration'])
        
        # Pretty print and save
        xml_str = ET.tostring(rss, encoding='utf-8')
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent='  ', encoding='utf-8')
        
        with open(self.rss_file, 'wb') as f:
            f.write(pretty_xml)
        
        logger.info(f"✅ RSS feed generated: {self.rss_file}")
        logger.info(f"📡 Total episodes in feed: {len(self.episodes)}")
        
        return self.rss_file
    
    def publish_episode(self, audio_path: str, title: str, description: str,
                       auto_upload_audio: bool = True) -> Dict[str, Any]:
        """Publish new podcast episode (fully automated!)
        
        Args:
            audio_path: Local path to audio file
            title: Episode title
            description: Episode description
            auto_upload_audio: If True, attempts to upload to Firebase
            
        Returns:
            Dictionary with publication result
        """
        try:
            logger.info(f"🎙️ Publishing episode: {title}")
            
            # Step 1: Upload audio to get public URL
            audio_url = None
            if auto_upload_audio:
                audio_url = self.upload_to_firebase(audio_path)
            
            if not audio_url:
                # Use local file path as placeholder - user will need to host it
                filename = os.path.basename(audio_path)
                audio_url = f"{self.podcast_config.get('website', 'https://your-site.com')}/podcast_audio/{filename}"
                logger.warning(f"⚠️ Using placeholder URL: {audio_url}")
                logger.warning(f"📤 You need to upload {audio_path} to your web hosting")
                logger.warning(f"    and make it accessible at: {audio_url}")
            
            # Step 2: Add to RSS feed
            self.add_episode_to_rss(audio_url, title, description)
            
            # Step 3: Regenerate RSS feed
            rss_path = self.generate_rss_feed()
            
            # Step 4: Try to upload RSS feed to Firebase
            if auto_upload_audio:
                self._upload_rss_to_firebase(rss_path)
            
            logger.info(f"")
            logger.info(f"✅ EPISODE PUBLISHED TO RSS FEED!")
            logger.info(f"")
            logger.info(f"📡 RSS Feed: {rss_path}")
            logger.info(f"🌐 RSS URL (once hosted): {self.podcast_config.get('rss_url')}")
            logger.info(f"")
            logger.info(f"📤 Next Steps:")
            logger.info(f"   1. Upload {rss_path} to your web hosting at:")
            logger.info(f"      {self.podcast_config.get('rss_url')}")
            if not audio_url.startswith('http://') and not audio_url.startswith('https://storage.googleapis'):
                logger.info(f"   2. Upload {audio_path} to:")
                logger.info(f"      {audio_url}")
            logger.info(f"")
            logger.info(f"🎯 One-Time Spotify Setup (if not done yet):")
            logger.info(f"   1. Go to: https://podcasters.spotify.com/")
            logger.info(f"   2. Click 'Get Started' > 'Import podcast'")
            logger.info(f"   3. Enter RSS feed URL: {self.podcast_config.get('rss_url')}")
            logger.info(f"   4. Spotify will automatically check for new episodes!")
            logger.info(f"")
            logger.info(f"🔄 Future episodes will appear automatically when RSS updates")
            
            return {
                "platform": "Podcast RSS Feed",
                "success": True,
                "automated": True,
                "audio_url": audio_url,
                "rss_feed": rss_path,
                "rss_url": self.podcast_config.get('rss_url'),
                "title": title,
                "episode_count": len(self.episodes),
                "needs_manual_upload": not audio_url.startswith('https://storage.googleapis')
            }
            
        except Exception as e:
            logger.error(f"Failed to publish episode: {e}")
            import traceback
            traceback.print_exc()
            return {
                "platform": "Podcast RSS Feed",
                "success": False,
                "error": str(e)
            }
    
    def _upload_rss_to_firebase(self, rss_path: str):
        """Upload RSS feed to Firebase Storage"""
        try:
            from firebase_admin import storage
            bucket = storage.bucket()
            blob = bucket.blob('podcast_feed.xml')
            # Include charset to ensure readers decode correctly
            blob.upload_from_filename(rss_path, content_type='application/rss+xml; charset=utf-8')
            blob.make_public()
            logger.info(f"✅ RSS feed uploaded to Firebase")
        except Exception as e:
            logger.warning(f"Could not upload RSS to Firebase: {e}")
