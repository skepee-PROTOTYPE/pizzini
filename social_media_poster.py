"""
Social Media Posting Utilities
Handles posting to X (Twitter) and Instagram with proper formatting
"""

import tweepy
import instagrapi
from typing import Optional, Dict, Any, List
import os
import logging
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from content_formatter import ContentFormatter
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import Azure Speech SDK
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_TTS_AVAILABLE = True
except ImportError:
    AZURE_TTS_AVAILABLE = False
    logger.info("Azure TTS not available - using gTTS only")

# Try to import Coqui TTS
try:
    from TTS.api import TTS as CoquiTTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False
    logger.info("Coqui TTS not available - install with: pip install TTS")

# Try to import gTTS
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    logger.info("gTTS not available - install with: pip install gTTS")

# Try to import pydub for audio duration (optional)
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    PYDUB_AVAILABLE = False
    logger.warning("pydub not fully compatible with Python 3.13 - audio duration will not be available")

class XPoster:
    """Handles posting to X (formerly Twitter) using Tweepy"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """Initialize X API client"""
        try:
            # Twitter API v2 client
            self.client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret,
                wait_on_rate_limit=True
            )
            
            # Twitter API v1.1 for media upload
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
            self.api_v1 = tweepy.API(auth)
            
            logger.info("X (Twitter) client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize X client: {e}")
            raise
    
    def post_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Post text to X"""
        try:
            # X has a 280 character limit
            if len(text) > 280:
                text = text[:277] + "..."
            
            response = self.client.create_tweet(text=text)
            logger.info(f"Successfully posted to X: {response.data['id']}")
            return {"platform": "X", "id": response.data['id'], "success": True}
        except Exception as e:
            logger.error(f"Failed to post to X: {e}")
            return {"platform": "X", "success": False, "error": str(e)}
    
    def post_with_image(self, text: str, image_path: str) -> Optional[Dict[str, Any]]:
        """Post text with image to X"""
        try:
            # Upload media first
            media = self.api_v1.media_upload(image_path)
            
            # Post tweet with media
            if len(text) > 280:
                text = text[:277] + "..."
            
            response = self.client.create_tweet(text=text, media_ids=[media.media_id])
            logger.info(f"Successfully posted to X with image: {response.data['id']}")
            return {"platform": "X", "id": response.data['id'], "success": True}
        except Exception as e:
            logger.error(f"Failed to post to X with image: {e}")
            return {"platform": "X", "success": False, "error": str(e)}

class FacebookPoster:
    """Handles posting to Facebook Pages using Graph API"""
    
    def __init__(self, page_access_token: str, page_id: str):
        """Initialize Facebook Page poster
        
        Args:
            page_access_token: Long-lived page access token
            page_id: Facebook Page ID
        """
        self.access_token = page_access_token
        self.page_id = page_id
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        logger.info("Facebook Page poster initialized")
    
    def post_text(self, text: str, link: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Post text to Facebook Page
        
        Args:
            text: Post content
            link: Optional URL to include
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/feed"
            params = {
                'message': text,
                'access_token': self.access_token
            }
            
            if link:
                params['link'] = link
            
            response = requests.post(endpoint, data=params)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully posted to Facebook: {result.get('id')}")
            return {"platform": "Facebook", "id": result.get('id'), "success": True}
        except Exception as e:
            logger.error(f"Failed to post to Facebook: {e}")
            return {"platform": "Facebook", "success": False, "error": str(e)}
    
    def post_photo(self, image_path: str, caption: str) -> Optional[Dict[str, Any]]:
        """Post photo to Facebook Page
        
        Args:
            image_path: Path to image file
            caption: Photo caption
        """
        try:
            endpoint = f"{self.base_url}/{self.page_id}/photos"
            
            with open(image_path, 'rb') as image_file:
                files = {'source': image_file}
                params = {
                    'message': caption,
                    'access_token': self.access_token
                }
                
                response = requests.post(endpoint, data=params, files=files)
                response.raise_for_status()
            
            result = response.json()
            logger.info(f"Successfully posted photo to Facebook: {result.get('id')}")
            return {"platform": "Facebook", "id": result.get('id'), "success": True}
        except Exception as e:
            logger.error(f"Failed to post photo to Facebook: {e}")
            return {"platform": "Facebook", "success": False, "error": str(e)}

class InstagramPoster:
    """Handles posting to Instagram using instagrapi"""
    
    def __init__(self, username: str, password: str, session_file: str = "instagram_session.json"):
        """Initialize Instagram client with session persistence"""
        try:
            self.client = instagrapi.Client()
            self.session_file = session_file
            
            # Try to load existing session
            if os.path.exists(session_file):
                try:
                    self.client.load_settings(session_file)
                    self.client.login(username, password)
                    logger.info("Instagram client initialized with saved session")
                except Exception as e:
                    logger.warning(f"Failed to load session, creating new: {e}")
                    self.client = instagrapi.Client()
                    self.client.login(username, password)
                    self.client.dump_settings(session_file)
            else:
                # First time login
                self.client.login(username, password)
                self.client.dump_settings(session_file)
                logger.info("Instagram client initialized and session saved")
        except Exception as e:
            logger.error(f"Failed to initialize Instagram client: {e}")
            raise
    
    def post_image_with_caption(self, image_path: str, caption: str) -> Optional[Dict[str, Any]]:
        """Post image with caption to Instagram"""
        try:
            # Instagram requires an image for posts
            media = self.client.photo_upload(image_path, caption)
            logger.info(f"Successfully posted to Instagram: {media.pk}")
            return {"platform": "Instagram", "id": media.pk, "success": True}
        except Exception as e:
            logger.error(f"Failed to post to Instagram: {e}")
            return {"platform": "Instagram", "success": False, "error": str(e)}
    
    def post_story(self, image_path: str) -> Optional[Dict[str, Any]]:
        """Post to Instagram story"""
        try:
            media = self.client.photo_upload_to_story(image_path)
            logger.info(f"Successfully posted Instagram story: {media.pk}")
            return {"platform": "Instagram Story", "id": media.pk, "success": True}
        except Exception as e:
            logger.error(f"Failed to post Instagram story: {e}")
            return {"platform": "Instagram Story", "success": False, "error": str(e)}

class AudioGenerator:
    """Generates audio files from text using Coqui TTS (free), Google TTS, or Azure TTS"""
    
    # Available Coqui TTS models for Italian (FREE, HIGH QUALITY)
    COQUI_VOICE_OPTIONS = {
        'priest-old-1': {
            'model': 'tts_models/it/mai_male/glow-tts',
            'description': '🎙️ FREE Old Priest #1 - Deep, contemplative Italian male (Traditional)',
            'speed': 0.85,
            'character': 'old_priest'
        },
        'priest-old-2': {
            'model': 'tts_models/it/mai_male/glow-tts',
            'description': '🎙️ FREE Old Priest #2 - Wise, authoritative Italian elder',
            'speed': 0.88,
            'character': 'elder_wise'
        },
        'priest-warm': {
            'model': 'tts_models/it/mai_male/glow-tts',
            'description': '🎙️ FREE Warm Priest - Compassionate, gentle Italian male',
            'speed': 0.92,
            'character': 'warm_priest'
        },
        'coqui-it-male': {
            'model': 'tts_models/it/mai_male/glow-tts',
            'description': '🎙️ FREE Italian Male - Standard neutral voice',
            'speed': 1.0,
            'character': 'neutral'
        },
        'coqui-it-female': {
            'model': 'tts_models/it/mai_female/glow-tts',
            'description': '🎙️ FREE Italian Female - Warm female voice',
            'speed': 1.0,
            'character': 'neutral'
        },
    }
    
    # Available gTTS language/accent options for Italian
    GTTS_VOICE_OPTIONS = {
        'gtts-it-male-slow': {'lang': 'it', 'tld': 'com', 'slow': True, 'description': 'gTTS: Italian Male (Slower, deliberate - good for old priest)'},
        'gtts-it-male': {'lang': 'it', 'tld': 'com', 'slow': False, 'description': 'gTTS: Italian Male (Normal speed)'},
        'gtts-it-male-it': {'lang': 'it', 'tld': 'it', 'slow': True, 'description': 'gTTS: Italian Male Italy (Slower, traditional)'},
        'gtts-it-male-uk': {'lang': 'it', 'tld': 'co.uk', 'slow': True, 'description': 'gTTS: Italian Male UK (Slower, deeper)'},
        'gtts-it-female': {'lang': 'it', 'tld': 'it', 'slow': False, 'description': 'gTTS: Italian Female (Standard)'},
    }
    
    # Azure Neural Voices for Italian (high quality, natural)
    AZURE_VOICE_OPTIONS = {
        'azure-diego': {'voice': 'it-IT-DiegoNeural', 'description': 'Azure: Diego - Mature male voice (best for priest)'},
        'azure-benigno': {'voice': 'it-IT-BenignoNeural', 'description': 'Azure: Benigno - Warm male voice'},
        'azure-calimero': {'voice': 'it-IT-CalimeroNeural', 'description': 'Azure: Calimero - Authoritative male'},
        'azure-elsa': {'voice': 'it-IT-ElsaNeural', 'description': 'Azure: Elsa - Female voice'},
        'azure-isabella': {'voice': 'it-IT-IsabellaNeural', 'description': 'Azure: Isabella - Female voice'},
    }
    
    def __init__(self, voice: str = 'priest-old-1', output_dir: str = "audio_output", 
                 azure_key: str = None, azure_region: str = None,
                 azure_pitch: str = '-8%', azure_rate: str = '0.90'):
        """Initialize audio generator
        
        Args:
            voice: Voice selection key from COQUI_VOICE_OPTIONS, GTTS_VOICE_OPTIONS or AZURE_VOICE_OPTIONS
            output_dir: Directory to save generated audio files
            azure_key: Azure Speech API key (required for Azure voices)
            azure_region: Azure region (e.g., 'westeurope', required for Azure voices)
            azure_pitch: Pitch adjustment for Azure voices (e.g., '-10%' for deeper, older sound)
            azure_rate: Speed adjustment for Azure voices (e.g., '0.88' for slower, contemplative)
        """
        self.voice = voice
        self.output_dir = output_dir
        self.azure_key = azure_key
        self.azure_region = azure_region
        self.azure_pitch = azure_pitch
        self.azure_rate = azure_rate
        self.coqui_model = None
        
        # Determine which TTS service to use
        if voice.startswith('azure-'):
            if not AZURE_TTS_AVAILABLE:
                raise ImportError("Azure TTS not available. Install: pip install azure-cognitiveservices-speech")
            if not azure_key or not azure_region:
                raise ValueError("Azure key and region required for Azure voices")
            self.tts_service = 'azure'
            voice_desc = self.AZURE_VOICE_OPTIONS.get(voice, {}).get('description', voice)
        elif voice in self.COQUI_VOICE_OPTIONS:
            if not COQUI_TTS_AVAILABLE:
                raise ImportError("Coqui TTS not available. Install: pip install TTS")
            self.tts_service = 'coqui'
            voice_config = self.COQUI_VOICE_OPTIONS[voice]
            voice_desc = voice_config['description']
            # Initialize Coqui model (lazy loading)
            logger.info(f"Loading Coqui TTS model: {voice_config['model']}...")
            self.coqui_model = CoquiTTS(voice_config['model'])
        elif voice.startswith('gtts-'):
            if not GTTS_AVAILABLE:
                raise ImportError("gTTS not available. Install: pip install gTTS")
            self.tts_service = 'gtts'
            voice_desc = self.GTTS_VOICE_OPTIONS.get(voice, self.GTTS_VOICE_OPTIONS['gtts-it-male-slow'])['description']
        else:
            # Default to Coqui if available, fall back to gTTS
            if COQUI_TTS_AVAILABLE:
                self.voice = 'priest-old-1'
                self.tts_service = 'coqui'
                voice_config = self.COQUI_VOICE_OPTIONS['priest-old-1']
                voice_desc = voice_config['description']
                logger.info(f"Loading Coqui TTS model: {voice_config['model']}...")
                self.coqui_model = CoquiTTS(voice_config['model'])
            else:
                self.voice = 'gtts-it-male-slow'
                self.tts_service = 'gtts'
                voice_desc = 'gTTS: Italian Male (Slower)'
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        logger.info(f"Audio generator initialized with: {voice_desc}")
    
    def text_to_speech(self, text: str, title: str = "audio", add_intro: bool = False) -> str:
        """Convert text to speech and save as MP3
        
        Args:
            text: Text content to convert (goes directly to audio, no modifications)
            title: Title for the audio file (used in filename only, not spoken)
            add_intro: Whether to add an intro phrase (default False)
            
        Returns:
            Path to generated audio file
        """
        try:
            # Use text as-is, no intro by default
            full_text = text
            if add_intro:
                full_text = f"{title}. {text}"
            
            # Create filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))[:50]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            service_prefix = 'azure' if self.tts_service == 'azure' else 'gtts'
            filename = f"{safe_title}_{service_prefix}_{timestamp}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            
            # Generate speech based on service
            if self.tts_service == 'azure':
                self._generate_azure_speech(full_text, filepath)
            elif self.tts_service == 'coqui':
                self._generate_coqui_speech(full_text, filepath)
            else:
                self._generate_gtts_speech(full_text, filepath)
            
            logger.info(f"Generated audio file: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to generate audio: {e}")
            raise
    
    def _generate_coqui_speech(self, text: str, filepath: str):
        """Generate speech using Coqui TTS (free, high quality)"""
        voice_config = self.COQUI_VOICE_OPTIONS[self.voice]
        
        # Generate speech with Coqui
        wav_filepath = filepath.replace('.mp3', '.wav')
        self.coqui_model.tts_to_file(
            text=text,
            file_path=wav_filepath,
            speed=voice_config.get('speed', 1.0)
        )
        
        # Convert WAV to MP3 if pydub is available
        if PYDUB_AVAILABLE:
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_wav(wav_filepath)
                audio.export(filepath, format='mp3', bitrate='128k')
                os.remove(wav_filepath)  # Clean up WAV file
            except Exception as e:
                logger.warning(f"Could not convert to MP3: {e}. Keeping WAV file.")
                # Rename WAV to MP3 path for consistency
                if os.path.exists(wav_filepath):
                    os.rename(wav_filepath, filepath.replace('.mp3', '.wav'))
        else:
            # Keep WAV format if pydub not available
            logger.info(f"pydub not available - audio saved as WAV format")
    
    def _generate_gtts_speech(self, text: str, filepath: str):
        """Generate speech using Google TTS"""
        voice_config = self.GTTS_VOICE_OPTIONS.get(self.voice, self.GTTS_VOICE_OPTIONS['gtts-it-male-slow'])
        
        tts = gTTS(
            text=text,
            lang=voice_config['lang'],
            tld=voice_config['tld'],
            slow=voice_config.get('slow', False)
        )
        tts.save(filepath)
    
    def _generate_azure_speech(self, text: str, filepath: str):
        """Generate speech using Azure Cognitive Services with SSML for expression"""
        speech_config = speechsdk.SpeechConfig(subscription=self.azure_key, region=self.azure_region)
        
        # Get voice name from configuration
        voice_config = self.AZURE_VOICE_OPTIONS[self.voice]
        voice_name = voice_config['voice']
        
        # Create SSML with prosody adjustments for old priest voice
        ssml_text = f"""
        <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='it-IT'>
            <voice name='{voice_name}'>
                <prosody rate='{self.azure_rate}' pitch='{self.azure_pitch}'>
                    {text}
                </prosody>
            </voice>
        </speak>
        """
        
        # Configure output to file
        audio_config = speechsdk.audio.AudioOutputConfig(filename=filepath)
        
        # Create synthesizer and generate speech
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise Exception(f"Azure TTS failed: {result.reason}")
    
    def create_podcast_episode(self, title: str, content: str, date: str = "") -> Dict[str, str]:
        """Create a podcast-ready audio file with metadata
        
        Args:
            title: Episode title
            content: Episode content (will be read directly, no intro)
            date: Publication date (not used in audio, only in metadata)
            
        Returns:
            Dictionary with audio file path and metadata
        """
        try:
            # Generate audio directly from content, no intro or date
            audio_path = self.text_to_speech(content, title, add_intro=False)
            
            return {
                'audio_path': audio_path,
                'title': title,
                'date': date,
                'duration': self._get_audio_duration(audio_path),
                'format': 'mp3'
            }
            
        except Exception as e:
            logger.error(f"Failed to create podcast episode: {e}")
            raise
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds"""
        if not PYDUB_AVAILABLE:
            logger.debug("pydub not available - cannot get audio duration")
            return 0.0
        
        try:
            audio = AudioSegment.from_mp3(audio_path)
            return len(audio) / 1000.0  # Convert milliseconds to seconds
        except Exception as e:
            logger.warning(f"Could not get audio duration: {e}")
            return 0.0
    
    @classmethod
    def list_available_voices(cls) -> List[Dict[str, str]]:
        """List all available voice options"""
        voices = []
        
        # Add Coqui TTS voices (FREE, RECOMMENDED)
        if COQUI_TTS_AVAILABLE:
            for key, config in cls.COQUI_VOICE_OPTIONS.items():
                voices.append({'key': key, 'service': '🆓 Coqui TTS (FREE - Recommended)', **config})
        
        # Add gTTS voices
        if GTTS_AVAILABLE:
            for key, config in cls.GTTS_VOICE_OPTIONS.items():
                voices.append({'key': key, 'service': '🆓 gTTS (Free)', **config})
        
        # Add Azure voices if available
        if AZURE_TTS_AVAILABLE:
            for key, config in cls.AZURE_VOICE_OPTIONS.items():
                voices.append({'key': key, 'service': '💰 Azure (Paid - Requires API key)', **config})
        
        return voices

class SpotifyPodcastPoster:
    """Prepares audio episodes for manual upload to Anchor/Spotify for Podcasters"""
    
    def __init__(self, anchor_email: str, anchor_password: str):
        """Initialize Spotify Podcast poster for Anchor
        
        Note: Generates audio files ready for manual upload to Anchor.fm
        
        Args:
            anchor_email: Anchor account email (for reference)
            anchor_password: Anchor account password (for reference)
        """
        self.email = anchor_email
        self.password = anchor_password
        logger.info("Spotify Podcast file generator initialized (manual upload to Anchor)")
    
    def upload_episode(self, audio_path: str, title: str, description: str, 
                       publish: bool = True) -> Optional[Dict[str, Any]]:
        """Prepare podcast episode for manual upload to Anchor/Spotify for Podcasters
        
        Args:
            audio_path: Path to audio file (MP3)
            title: Episode title
            description: Episode description
            publish: Whether to mark as ready to publish (True) or draft (False)
        
        Returns:
            Dictionary with preparation result
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")
            
            logger.info(f"📝 Preparing episode for Anchor upload: {title}")
            logger.info(f"🎵 Audio file: {audio_path}")
            
            # Save metadata for manual upload
            metadata = {
                'anchor_email': self.email,
                'audio_path': os.path.abspath(audio_path),
                'title': title,
                'description': description,
                'publish_immediately': publish,
                'created_time': datetime.now().isoformat(),
                'status': 'ready_for_manual_upload',
                'instructions': [
                    f"1. Go to https://anchor.fm/dashboard/episode/new",
                    f"2. Upload this audio file: {os.path.abspath(audio_path)}",
                    f"3. Title: {title}",
                    f"4. Description: {description}",
                    f"5. Click 'Save' or 'Publish' as needed"
                ]
            }
            
            metadata_path = audio_path.replace('.mp3', '_upload_instructions.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Episode ready for upload!")
            logger.info(f"📄 Upload instructions saved: {metadata_path}")
            logger.info(f"")
            logger.info(f"🔗 To upload: Go to https://anchor.fm/dashboard/episode/new")
            logger.info(f"   Upload file: {os.path.abspath(audio_path)}")
            
            return {
                "platform": "Spotify/Anchor",
                "success": True,
                "ready_for_upload": True,
                "audio_path": os.path.abspath(audio_path),
                "metadata_path": metadata_path,
                "title": title,
                "upload_url": "https://anchor.fm/dashboard/episode/new"
            }
            
        except Exception as e:
            logger.error(f"Failed to prepare episode: {e}")
            return {
                "platform": "Spotify/Anchor",
                "success": False,
                "error": str(e)
            }

class ImageGenerator:
    """Generates images for social media posts"""
    
    def __init__(self, width: int = 1080, height: int = 1080):
        self.width = width
        self.height = height
        self.background_color = (255, 255, 255)  # White background
        self.text_color = (51, 51, 51)  # Dark gray text
        self.accent_color = (74, 144, 226)  # Blue accent
    
    def create_quote_image(self, title: str, content: str, date: str = "", save_path: str = "temp_post.png") -> str:
        """Create a quote image for Instagram/X"""
        try:
            # Create image
            img = Image.new('RGB', (self.width, self.height), self.background_color)
            draw = ImageDraw.Draw(img)
            
            # Try to load a nice font, fallback to default
            try:
                title_font = ImageFont.truetype("arial.ttf", 48)
                content_font = ImageFont.truetype("arial.ttf", 32)
                date_font = ImageFont.truetype("arial.ttf", 24)
            except:
                title_font = ImageFont.load_default()
                content_font = ImageFont.load_default()
                date_font = ImageFont.load_default()
            
            # Calculate margins
            margin = 80
            max_width = self.width - (2 * margin)
            
            # Draw title
            title_y = margin
            wrapped_title = self._wrap_text(title, title_font, max_width)
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                line_width = bbox[2] - bbox[0]
                x = (self.width - line_width) // 2
                draw.text((x, title_y), line, font=title_font, fill=self.accent_color)
                title_y += bbox[3] - bbox[1] + 10
            
            # Add some space after title
            content_y = title_y + 40
            
            # Draw content
            wrapped_content = self._wrap_text(content[:500] + "..." if len(content) > 500 else content, 
                                            content_font, max_width)
            for line in wrapped_content:
                if content_y > self.height - 200:  # Leave space for date
                    break
                bbox = draw.textbbox((0, 0), line, font=content_font)
                line_width = bbox[2] - bbox[0]
                x = (self.width - line_width) // 2
                draw.text((x, content_y), line, font=content_font, fill=self.text_color)
                content_y += bbox[3] - bbox[1] + 15
            
            # Draw date at bottom
            if date:
                date_bbox = draw.textbbox((0, 0), date, font=date_font)
                date_width = date_bbox[2] - date_bbox[0]
                date_x = (self.width - date_width) // 2
                date_y = self.height - margin - 30
                draw.text((date_x, date_y), date, font=date_font, fill=self.text_color)
            
            # Save image
            img.save(save_path, 'PNG', quality=95)
            logger.info(f"Generated image saved to {save_path}")
            return save_path
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}")
            raise
    
    def _wrap_text(self, text: str, font, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = font.getbbox(test_line)
            if bbox[2] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                    current_line = word
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(current_line)
        
        return lines

class SocialMediaManager:
    """Main class to manage posting across platforms"""
    
    def __init__(self, audio_voice: str = 'it-female'):
        self.x_poster = None
        self.instagram_poster = None
        self.facebook_poster = None
        self.spotify_poster = None
        self.image_generator = ImageGenerator()
        self.content_formatter = ContentFormatter()
        self.audio_generator = AudioGenerator(voice=audio_voice)
    
    def setup_x(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """Setup X (Twitter) posting"""
        self.x_poster = XPoster(api_key, api_secret, access_token, access_token_secret)
    
    def setup_instagram(self, username: str, password: str):
        """Setup Instagram posting"""
        self.instagram_poster = InstagramPoster(username, password)
    
    def setup_facebook(self, page_access_token: str, page_id: str):
        """Setup Facebook Page posting"""
        self.facebook_poster = FacebookPoster(page_access_token, page_id)
    
    def setup_spotify_podcast(self, config_path: str = 'config.json'):
        """Setup automated Spotify Podcast posting via RSS feed
        
        Args:
            config_path: Path to configuration file with podcast info
        """
        from automated_podcast_publisher import AutomatedPodcastPublisher
        self.spotify_poster = AutomatedPodcastPublisher(config_path)
        logger.info("Automated podcast publisher initialized (RSS feed method)")
    
    def change_audio_voice(self, voice: str):
        """Change the audio generation voice
        
        Args:
            voice: Voice key from AudioGenerator.VOICE_OPTIONS
        """
        self.audio_generator = AudioGenerator(voice=voice)
        logger.info(f"Changed audio voice to: {voice}")
    
    def post_to_all_platforms(self, title: str, content: str, date: str = "", 
                             include_image: bool = True, include_audio: bool = False) -> list:
        """Post content to all configured platforms
        
        Args:
            title: Content title
            content: Main content text
            date: Publication date
            include_image: Whether to generate and post images
            include_audio: Whether to generate audio for podcast
        """
        results = []
        
        # Generate image if needed
        image_path = None
        if include_image:
            try:
                image_path = self.image_generator.create_quote_image(title, content, date)
            except Exception as e:
                logger.warning(f"Failed to generate image: {e}")
                include_image = False
        
        # Generate audio if needed
        audio_path = None
        if include_audio:
            try:
                episode_data = self.audio_generator.create_podcast_episode(title, content, date)
                audio_path = episode_data['audio_path']
                logger.info(f"Generated audio: {audio_path} ({episode_data['duration']:.1f}s)")
            except Exception as e:
                logger.warning(f"Failed to generate audio: {e}")
                include_audio = False
        
        # Post to X
        if self.x_poster:
            x_text = f"{title}\n\n{content[:200]}..." if len(content) > 200 else f"{title}\n\n{content}"
            if include_image and image_path:
                result = self.x_poster.post_with_image(x_text, image_path)
            else:
                result = self.x_poster.post_text(x_text)
            results.append(result)
        
        # Post to Instagram
        if self.instagram_poster and include_image and image_path:
            instagram_formatted = self.content_formatter.format_for_platform(
                title=title,
                content=content,
                platform='instagram',
                date=date,
                include_hashtags=True
            )
            instagram_caption = instagram_formatted['text']
            result = self.instagram_poster.post_image_with_caption(image_path, instagram_caption)
            results.append(result)
        
        # Post to Facebook
        if self.facebook_poster:
            if include_image and image_path:
                facebook_formatted = self.content_formatter.format_for_platform(
                    title=title,
                    content=content,
                    platform='facebook',
                    date=date,
                    include_hashtags=True
                )
                result = self.facebook_poster.post_photo(image_path, facebook_formatted['text'])
            else:
                fb_text = f"{title}\n\n{content}"
                result = self.facebook_poster.post_text(fb_text)
            results.append(result)
        
        # Post to Spotify/Anchor via RSS feed
        if self.spotify_poster and include_audio and audio_path:
            podcast_description = self.content_formatter.format_for_platform(
                title=title,
                content=content,
                platform='linkedin',  # Using LinkedIn format for cleaner description
                date=date,
                include_hashtags=False
            )['text']
            result = self.spotify_poster.publish_episode(audio_path, title, podcast_description)
            results.append(result)
        
        # Clean up temporary image
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except:
                pass
        
        return results

# Example usage
if __name__ == "__main__":
    # This would normally be used with proper credentials
    manager = SocialMediaManager()
    
    # Example of how to use (credentials would come from config)
    # manager.setup_x("api_key", "api_secret", "access_token", "access_token_secret")
    # manager.setup_instagram("username", "password")
    
    # Test image generation
    image_gen = ImageGenerator()
    test_image = image_gen.create_quote_image(
        "AIUTO PER IL PIZZINO (1°)",
        "La parola rapporto dice che una cosa c'entra con un'altra...",
        "17.09.2012"
    )
    print(f"Test image created: {test_image}")