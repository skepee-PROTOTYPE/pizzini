#!/usr/bin/env python3
"""
Pizzini Social Media Automation
Main script to automate social media posting of Italian philosophical content

Usage:
    python main.py --setup          # Interactive setup
    python main.py --post-now <id>  # Post specific entry immediately  
    python main.py --start          # Start automated scheduling
    python main.py --status         # Show status and next posts
    python main.py --test           # Test posting without actually posting
"""

import argparse
import sys
import os
import logging
from datetime import datetime
from typing import List, Optional

# Import our modules
from xml_parser import PizziniXMLParser, PizziniEntry
from social_media_poster import SocialMediaManager
from content_formatter import ContentFormatter
from scheduler import PostScheduler, PostingTimeOptimizer
from config_manager import ConfigManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pizzini_automation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PizziniAutomation:
    """Main automation class that coordinates all components"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.xml_parser = None
        self.social_media_manager = SocialMediaManager()
        self.content_formatter = ContentFormatter()
        self.scheduler = PostScheduler()
        self.entries: List[PizziniEntry] = []
        self.test_mode = False
        
    def initialize(self) -> bool:
        """Initialize the automation system"""
        try:
            # Load configuration
            if not self.config_manager.load_config():
                logger.error("Failed to load configuration")
                return False
            
            if not self.config_manager.validate_config():
                logger.error("Configuration validation failed")
                return False
            
            # Load XML content
            content_settings = self.config_manager.get_content_settings()
            xml_file = content_settings.get('xml_file_path', 'pizzinifile.xml')
            
            if not os.path.exists(xml_file):
                logger.error(f"XML file not found: {xml_file}")
                return False
            
            self.xml_parser = PizziniXMLParser(xml_file)
            self.entries = self.xml_parser.parse()
            
            if not self.entries:
                logger.error("No content entries found in XML file")
                return False
            
            logger.info(f"Loaded {len(self.entries)} content entries")
            
            # Setup social media platforms
            self._setup_social_media()
            
            # Setup scheduler callback
            self.scheduler.set_post_callback(self._post_entry_callback)
            
            logger.info("Automation system initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize automation system: {e}")
            return False
    
    def _setup_social_media(self):
        """Setup social media platform connections"""
        enabled_platforms = self.config_manager.get_enabled_platforms()
        
        for platform in enabled_platforms:
            config = self.config_manager.get_platform_config(platform)
            
            try:
                if platform == 'twitter':
                    self.social_media_manager.setup_x(
                        config['api_key'],
                        config['api_secret'],
                        config['access_token'],
                        config['access_token_secret']
                    )
                    logger.info("Twitter/X configured successfully")
                
                elif platform == 'instagram':
                    self.social_media_manager.setup_instagram(
                        config['username'],
                        config['password']
                    )
                    logger.info("Instagram configured successfully")
                
                # Add other platforms as needed
                
            except Exception as e:
                logger.error(f"Failed to setup {platform}: {e}")
    
    def _post_entry_callback(self, entry_id: int, platforms: List[str]) -> bool:
        """Callback function for scheduled posts"""
        try:
            entry = self.xml_parser.get_entry_by_id(entry_id)
            if not entry:
                logger.error(f"Entry {entry_id} not found")
                return False
            
            return self.post_entry(entry, platforms)
            
        except Exception as e:
            logger.error(f"Error in post callback for entry {entry_id}: {e}")
            return False
    
    def post_entry(self, entry: PizziniEntry, platforms: Optional[List[str]] = None) -> bool:
        """Post a single entry to specified platforms"""
        try:
            if platforms is None:
                posting_settings = self.config_manager.get_posting_settings()
                platforms = posting_settings.get('default_platforms', ['twitter'])
            
            logger.info(f"Posting entry {entry.id}: {entry.title}")
            
            if self.test_mode:
                logger.info("TEST MODE - Would post the following:")
                for platform in platforms:
                    formatted = self.content_formatter.format_for_platform(
                        entry.title, entry.content, platform, entry.date
                    )
                    logger.info(f"{platform.upper()}: {formatted['text'][:100]}...")
                return True
            
            # Post to all platforms
            results = self.social_media_manager.post_to_all_platforms(
                entry.title,
                entry.content,
                entry.date,
                include_image=self.config_manager.get_posting_settings().get('include_images', True)
            )
            
            # Log results
            success_count = sum(1 for result in results if result and result.get('success', False))
            total_count = len(results)
            
            logger.info(f"Posted to {success_count}/{total_count} platforms successfully")
            
            for result in results:
                if result:
                    status = "SUCCESS" if result.get('success', False) else "FAILED"
                    platform = result.get('platform', 'Unknown')
                    logger.info(f"{platform}: {status}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Failed to post entry {entry.id}: {e}")
            return False
    
    def start_automation(self) -> bool:
        """Start the automated posting system"""
        try:
            scheduling_settings = self.config_manager.get_scheduling_settings()
            
            if not scheduling_settings.get('enabled', False):
                logger.warning("Scheduling is disabled in configuration")
                return False
            
            content_settings = self.config_manager.get_content_settings()
            
            # Determine which entries to post
            entry_ids_to_post = content_settings.get('entry_ids_to_post', [])
            exclude_entry_ids = content_settings.get('exclude_entry_ids', [])
            
            if not entry_ids_to_post:
                # Use all entries if none specified
                entry_ids_to_post = [entry.id for entry in self.entries]
            
            # Remove excluded entries
            entry_ids_to_post = [eid for eid in entry_ids_to_post if eid not in exclude_entry_ids]
            
            if not entry_ids_to_post:
                logger.error("No entries available for posting")
                return False
            
            logger.info(f"Will post from {len(entry_ids_to_post)} entries")
            
            # Setup scheduling based on mode
            mode = scheduling_settings.get('mode', 'recurring')
            platforms = self.config_manager.get_posting_settings().get('default_platforms', ['twitter'])
            
            if mode == 'recurring':
                recurring_settings = scheduling_settings.get('recurring_settings', {})
                success = self.scheduler.schedule_recurring_posts(
                    entry_ids_to_post,
                    interval_days=recurring_settings.get('interval_days', 7),
                    start_time=recurring_settings.get('start_time', '09:00'),
                    platforms=platforms,
                    randomize=recurring_settings.get('randomize_time', False)
                )
            elif mode == 'random':
                random_settings = scheduling_settings.get('random_settings', {})
                success = self.scheduler.schedule_random_posts(
                    entry_ids_to_post,
                    posts_per_week=random_settings.get('posts_per_week', 3),
                    time_windows=random_settings.get('time_windows', [("09:00", "12:00"), ("15:00", "18:00")]),
                    platforms=platforms
                )
            else:
                logger.error(f"Unknown scheduling mode: {mode}")
                return False
            
            if not success:
                logger.error("Failed to setup scheduling")
                return False
            
            # Start the scheduler
            self.scheduler.start_scheduler()
            logger.info("Automation started successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to start automation: {e}")
            return False
    
    def stop_automation(self):
        """Stop the automated posting system"""
        self.scheduler.stop_scheduler()
        logger.info("Automation stopped")
    
    def get_status(self) -> dict:
        """Get current status of the automation system"""
        try:
            scheduler_status = self.scheduler.get_scheduler_status()
            
            status = {
                'initialized': len(self.entries) > 0,
                'total_entries': len(self.entries),
                'enabled_platforms': self.config_manager.get_enabled_platforms(),
                'scheduler_running': scheduler_status['running'],
                'total_scheduled_jobs': scheduler_status['total_jobs'],
                'next_posts': scheduler_status['next_posts'],
                'posted_content_count': scheduler_status['posted_content_count']
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {'error': str(e)}
    
    def test_posting(self, entry_id: Optional[int] = None):
        """Test posting functionality without actually posting"""
        self.test_mode = True
        
        if entry_id:
            entry = self.xml_parser.get_entry_by_id(entry_id)
            if entry:
                self.post_entry(entry)
            else:
                logger.error(f"Entry {entry_id} not found")
        else:
            # Test with first entry
            if self.entries:
                self.post_entry(self.entries[0])
        
        self.test_mode = False

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description='Pizzini Social Media Automation')
    parser.add_argument('--setup', action='store_true', help='Run interactive setup')
    parser.add_argument('--post-now', type=int, metavar='ID', help='Post specific entry immediately')
    parser.add_argument('--start', action='store_true', help='Start automated scheduling')
    parser.add_argument('--stop', action='store_true', help='Stop automated scheduling')
    parser.add_argument('--status', action='store_true', help='Show system status')
    parser.add_argument('--test', type=int, nargs='?', const=0, metavar='ID', help='Test posting (optional entry ID)')
    parser.add_argument('--list-entries', action='store_true', help='List all available entries')
    
    args = parser.parse_args()
    
    automation = PizziniAutomation()
    
    try:
        # Handle setup
        if args.setup:
            print("Starting interactive setup...")
            automation.config_manager.interactive_setup()
            print("Setup complete! You can now run the automation.")
            return
        
        # Initialize system for other operations
        if not automation.initialize():
            print("Failed to initialize automation system. Run --setup first.")
            sys.exit(1)
        
        # Handle different commands
        if args.list_entries:
            print(f"\nFound {len(automation.entries)} entries:")
            for entry in automation.entries:
                print(f"  {entry.id}: {entry.title} ({entry.date})")
            print()
        
        elif args.post_now is not None:
            entry = automation.xml_parser.get_entry_by_id(args.post_now)
            if entry:
                print(f"Posting entry {args.post_now}: {entry.title}")
                success = automation.post_entry(entry)
                print("Posted successfully!" if success else "Posting failed!")
            else:
                print(f"Entry {args.post_now} not found")
        
        elif args.test is not None:
            print("Testing posting functionality...")
            automation.test_posting(args.test if args.test > 0 else None)
            print("Test complete!")
        
        elif args.start:
            print("Starting automation...")
            success = automation.start_automation()
            if success:
                print("Automation started! Press Ctrl+C to stop.")
                try:
                    while True:
                        import time
                        time.sleep(10)
                        # Show status every 10 minutes
                        if datetime.now().minute % 10 == 0:
                            status = automation.get_status()
                            print(f"Status: {status['posted_content_count']} posts sent, "
                                  f"{status['total_scheduled_jobs']} jobs scheduled")
                except KeyboardInterrupt:
                    print("\nStopping automation...")
                    automation.stop_automation()
                    print("Automation stopped.")
            else:
                print("Failed to start automation!")
        
        elif args.stop:
            automation.stop_automation()
            print("Automation stopped.")
        
        elif args.status:
            status = automation.get_status()
            print("\n=== Pizzini Automation Status ===")
            print(f"Initialized: {status['initialized']}")
            print(f"Total entries: {status['total_entries']}")
            print(f"Enabled platforms: {', '.join(status['enabled_platforms'])}")
            print(f"Scheduler running: {status['scheduler_running']}")
            print(f"Scheduled jobs: {status['total_scheduled_jobs']}")
            print(f"Posts sent: {status['posted_content_count']}")
            
            if status['next_posts']:
                print("\nNext scheduled posts:")
                for post_info in status['next_posts']:
                    print(f"  {post_info['next_run']} - {post_info['tags']}")
            print()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        automation.stop_automation()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()