"""
Configuration Manager for Social Media Automation
Handles loading, validation, and secure storage of configuration settings
"""

import json
import os
from typing import Dict, Any, Optional
import logging
from cryptography.fernet import Fernet
import base64
import getpass

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration for the social media automation system"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.encryption_key: Optional[bytes] = None
        
    def load_config(self) -> bool:
        """Load configuration from file"""
        try:
            if not os.path.exists(self.config_file):
                logger.warning(f"Config file {self.config_file} not found. Creating from template...")
                return self._create_config_from_template()
            
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info(f"Configuration loaded from {self.config_file}")
            return True
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return False
    
    def _create_config_from_template(self) -> bool:
        """Create config.json from template"""
        try:
            template_file = "config_template.json"
            if os.path.exists(template_file):
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_config = json.load(f)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(template_config, f, indent=2)
                
                self.config = template_config
                logger.info(f"Created {self.config_file} from template")
                return True
            else:
                logger.error("Template file not found")
                return False
                
        except Exception as e:
            logger.error(f"Failed to create config from template: {e}")
            return False
    
    def validate_config(self) -> bool:
        """Validate the loaded configuration"""
        required_sections = ['social_media', 'posting_settings', 'content_settings']
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required config section: {section}")
                return False
        
        # Validate social media credentials
        enabled_platforms = []
        for platform, settings in self.config['social_media'].items():
            if settings.get('enabled', False):
                enabled_platforms.append(platform)
                if not self._validate_platform_config(platform, settings):
                    logger.warning(f"Invalid configuration for {platform}")
        
        if not enabled_platforms:
            logger.warning("No social media platforms enabled")
        else:
            logger.info(f"Enabled platforms: {', '.join(enabled_platforms)}")
        
        return True
    
    def _validate_platform_config(self, platform: str, settings: Dict[str, Any]) -> bool:
        """Validate configuration for a specific platform"""
        required_fields = {
            'twitter': ['api_key', 'api_secret', 'access_token', 'access_token_secret'],
            'instagram': ['username', 'password'],
            'facebook': ['page_access_token', 'page_id'],
            'linkedin': ['access_token']
        }
        
        platform_requirements = required_fields.get(platform, [])
        
        for field in platform_requirements:
            if not settings.get(field) or settings[field].startswith('YOUR_'):
                logger.warning(f"Missing or placeholder value for {platform}.{field}")
                return False
        
        return True
    
    def get_platform_config(self, platform: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific platform"""
        return self.config.get('social_media', {}).get(platform)
    
    def get_posting_settings(self) -> Dict[str, Any]:
        """Get posting settings"""
        return self.config.get('posting_settings', {})
    
    def get_scheduling_settings(self) -> Dict[str, Any]:
        """Get scheduling settings"""
        return self.config.get('scheduling', {})
    
    def get_content_settings(self) -> Dict[str, Any]:
        """Get content settings"""
        return self.config.get('content_settings', {})
    
    def get_enabled_platforms(self) -> list:
        """Get list of enabled platforms"""
        enabled = []
        for platform, settings in self.config.get('social_media', {}).items():
            if settings.get('enabled', False):
                enabled.append(platform)
        return enabled
    
    def update_config(self, section: str, key: str, value: Any) -> bool:
        """Update a configuration value"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            return self.save_config()
        except Exception as e:
            logger.error(f"Failed to update config: {e}")
            return False
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            return False
    
    def setup_encryption(self, password: Optional[str] = None) -> bool:
        """Setup encryption for sensitive data"""
        try:
            if not password:
                password = getpass.getpass("Enter password for credential encryption: ")
            
            # Generate key from password
            key = base64.urlsafe_b64encode(password.encode()[:32].ljust(32, b'0'))
            self.encryption_key = key
            
            logger.info("Encryption setup complete")
            return True
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            return False
    
    def encrypt_credentials(self) -> bool:
        """Encrypt sensitive credentials"""
        if not self.encryption_key:
            logger.error("Encryption not setup")
            return False
        
        try:
            fernet = Fernet(self.encryption_key)
            
            # Extract and encrypt credentials
            credentials = {}
            for platform, settings in self.config.get('social_media', {}).items():
                platform_creds = {}
                for key, value in settings.items():
                    if key in ['api_key', 'api_secret', 'access_token', 'access_token_secret', 
                              'username', 'password', 'page_access_token']:
                        if isinstance(value, str) and value and not value.startswith('YOUR_'):
                            platform_creds[key] = fernet.encrypt(value.encode()).decode()
                        else:
                            platform_creds[key] = value
                    else:
                        platform_creds[key] = value
                credentials[platform] = platform_creds
            
            # Save encrypted credentials
            with open('credentials.enc', 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
            
            logger.info("Credentials encrypted and saved")
            return True
        except Exception as e:
            logger.error(f"Failed to encrypt credentials: {e}")
            return False
    
    def decrypt_credentials(self) -> bool:
        """Decrypt and load credentials"""
        if not self.encryption_key:
            logger.error("Encryption not setup")
            return False
        
        try:
            if not os.path.exists('credentials.enc'):
                logger.error("Encrypted credentials file not found")
                return False
            
            fernet = Fernet(self.encryption_key)
            
            with open('credentials.enc', 'r', encoding='utf-8') as f:
                encrypted_creds = json.load(f)
            
            # Decrypt credentials
            for platform, settings in encrypted_creds.items():
                for key, value in settings.items():
                    if key in ['api_key', 'api_secret', 'access_token', 'access_token_secret', 
                              'username', 'password', 'page_access_token']:
                        if isinstance(value, str) and value and not value.startswith('YOUR_'):
                            try:
                                decrypted = fernet.decrypt(value.encode()).decode()
                                self.config['social_media'][platform][key] = decrypted
                            except:
                                # Value might not be encrypted
                                self.config['social_media'][platform][key] = value
            
            logger.info("Credentials decrypted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            return False
    
    def interactive_setup(self) -> bool:
        """Interactive setup for first-time configuration"""
        print("=== Social Media Automation Setup ===")
        print()
        
        # Initialize config structure if empty
        if not self.config:
            self.config = {
                'social_media': {},
                'posting_settings': {
                    'default_platforms': [],
                    'include_images': True,
                    'include_hashtags': True,
                    'max_hashtags_per_platform': {
                        'twitter': 2,
                        'instagram': 10,
                        'facebook': 3,
                        'linkedin': 3
                    }
                },
                'scheduling': {
                    'enabled': True
                },
                'content_settings': {
                    'xml_file_path': 'pizzinifile.xml',
                    'entry_ids_to_post': [],
                    'exclude_entry_ids': [],
                    'content_rotation': True
                }
            }
        
        platforms_to_setup = []
        
        # Ask which platforms to configure
        print("Which platforms would you like to configure?")
        for platform in ['twitter', 'instagram', 'facebook', 'linkedin']:
            response = input(f"Configure {platform.title()}? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                platforms_to_setup.append(platform)
        
        # Update default platforms
        self.config['posting_settings']['default_platforms'] = platforms_to_setup
        
        # Configure each platform
        for platform in platforms_to_setup:
            print(f"\n--- {platform.title()} Configuration ---")
            if platform == 'twitter':
                self._setup_twitter()
            elif platform == 'instagram':
                self._setup_instagram()
            elif platform == 'facebook':
                self._setup_facebook()
            elif platform == 'linkedin':
                self._setup_linkedin()
        
        # Configure scheduling
        print("\n--- Scheduling Configuration ---")
        self._setup_scheduling()
        
        return self.save_config()
    
    def _setup_twitter(self):
        """Interactive Twitter setup"""
        print("You'll need Twitter API credentials from https://developer.twitter.com/")
        
        api_key = input("Twitter API Key: ").strip()
        api_secret = input("Twitter API Secret: ").strip()
        access_token = input("Twitter Access Token: ").strip()
        access_token_secret = input("Twitter Access Token Secret: ").strip()
        
        # Ensure social_media section exists
        if 'social_media' not in self.config:
            self.config['social_media'] = {}
        
        self.config['social_media']['twitter'] = {
            'enabled': True,
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }
    
    def _setup_instagram(self):
        """Interactive Instagram setup"""
        print("Instagram requires username/password authentication")
        print("Note: This method may require 2FA handling")
        
        username = input("Instagram Username: ").strip()
        password = getpass.getpass("Instagram Password: ")
        
        # Ensure social_media section exists
        if 'social_media' not in self.config:
            self.config['social_media'] = {}
        
        self.config['social_media']['instagram'] = {
            'enabled': True,
            'username': username,
            'password': password
        }
    
    def _setup_facebook(self):
        """Interactive Facebook setup"""
        print("Facebook requires a Page Access Token from Facebook Developer Console")
        
        page_access_token = input("Facebook Page Access Token: ").strip()
        page_id = input("Facebook Page ID: ").strip()
        
        # Ensure social_media section exists
        if 'social_media' not in self.config:
            self.config['social_media'] = {}
        
        self.config['social_media']['facebook'] = {
            'enabled': True,
            'page_access_token': page_access_token,
            'page_id': page_id
        }
    
    def _setup_linkedin(self):
        """Interactive LinkedIn setup"""
        print("LinkedIn requires an access token from LinkedIn Developer Platform")
        
        access_token = input("LinkedIn Access Token: ").strip()
        
        # Ensure social_media section exists
        if 'social_media' not in self.config:
            self.config['social_media'] = {}
        
        self.config['social_media']['linkedin'] = {
            'enabled': True,
            'access_token': access_token
        }
    
    def _setup_scheduling(self):
        """Interactive scheduling setup"""
        print("Choose scheduling mode:")
        print("1. Recurring (post every X days)")
        print("2. Random (post X times per week at random times)")
        
        mode_choice = input("Enter choice (1 or 2): ").strip()
        
        # Ensure scheduling section exists
        if 'scheduling' not in self.config:
            self.config['scheduling'] = {}
        
        if mode_choice == '1':
            interval = int(input("Post every how many days? (default: 7): ") or 7)
            start_time = input("Start time (HH:MM, default: 09:00): ") or "09:00"
            
            self.config['scheduling'] = {
                'enabled': True,
                'mode': 'recurring',
                'recurring_settings': {
                    'interval_days': interval,
                    'start_time': start_time,
                    'randomize_time': False
                }
            }
        elif mode_choice == '2':
            posts_per_week = int(input("How many posts per week? (default: 3): ") or 3)
            
            self.config['scheduling'] = {
                'enabled': True,
                'mode': 'random',
                'random_settings': {
                    'posts_per_week': posts_per_week,
                    'time_windows': [
                        ["09:00", "12:00"],
                        ["15:00", "18:00"]
                    ]
                }
            }

# Example usage
if __name__ == "__main__":
    config_manager = ConfigManager()
    
    if not os.path.exists("config.json"):
        print("No configuration found. Starting interactive setup...")
        config_manager.interactive_setup()
    else:
        config_manager.load_config()
        config_manager.validate_config()
        
        print("Current enabled platforms:", config_manager.get_enabled_platforms())