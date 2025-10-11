"""
Scheduling System for Social Media Posts
Handles automated posting at specified times and intervals
"""

import schedule
import time
import threading
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Callable, Optional
import random

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostScheduler:
    """Handles scheduling of social media posts"""
    
    def __init__(self):
        self.scheduled_jobs = []
        self.running = False
        self.scheduler_thread = None
        self.post_callback = None
        self.posted_content_ids = set()  # Track posted content to avoid duplicates
        
    def set_post_callback(self, callback: Callable):
        """Set the callback function for posting content"""
        self.post_callback = callback
    
    def schedule_single_post(self, entry_id: int, post_time: datetime, 
                           platforms: List[str] = ['twitter', 'instagram']) -> bool:
        """Schedule a single post for a specific time"""
        try:
            def job():
                if self.post_callback and entry_id not in self.posted_content_ids:
                    logger.info(f"Executing scheduled post for entry {entry_id}")
                    result = self.post_callback(entry_id, platforms)
                    if result:
                        self.posted_content_ids.add(entry_id)
                    return result
                return False
            
            # Schedule the job
            schedule.every().day.at(post_time.strftime("%H:%M")).do(job).tag(f"single_post_{entry_id}")
            
            scheduled_job = {
                'type': 'single',
                'entry_id': entry_id,
                'time': post_time,
                'platforms': platforms,
                'job_tag': f"single_post_{entry_id}"
            }
            
            self.scheduled_jobs.append(scheduled_job)
            logger.info(f"Scheduled single post for entry {entry_id} at {post_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule single post: {e}")
            return False
    
    def schedule_recurring_posts(self, entry_ids: List[int], 
                               interval_days: int = 7,
                               start_time: str = "09:00",
                               platforms: List[str] = ['twitter', 'instagram'],
                               randomize: bool = True) -> bool:
        """Schedule recurring posts from a list of entries"""
        try:
            entry_index = 0
            
            def rotating_job():
                nonlocal entry_index
                if self.post_callback and entry_ids:
                    current_entry = entry_ids[entry_index % len(entry_ids)]
                    
                    # Skip if already posted recently
                    if current_entry in self.posted_content_ids:
                        entry_index += 1
                        current_entry = entry_ids[entry_index % len(entry_ids)]
                    
                    logger.info(f"Executing recurring post for entry {current_entry}")
                    result = self.post_callback(current_entry, platforms)
                    
                    if result:
                        self.posted_content_ids.add(current_entry)
                        # Remove from posted set after some time to allow reposting
                        threading.Timer(interval_days * 24 * 3600 * len(entry_ids), 
                                      lambda: self.posted_content_ids.discard(current_entry)).start()
                    
                    entry_index += 1
                    return result
                return False
            
            # Schedule recurring job
            if interval_days == 1:
                schedule.every().day.at(start_time).do(rotating_job).tag("recurring_daily")
            elif interval_days == 7:
                schedule.every().week.at(start_time).do(rotating_job).tag("recurring_weekly")
            else:
                schedule.every(interval_days).days.at(start_time).do(rotating_job).tag("recurring_custom")
            
            scheduled_job = {
                'type': 'recurring',
                'entry_ids': entry_ids,
                'interval_days': interval_days,
                'start_time': start_time,
                'platforms': platforms,
                'randomize': randomize,
                'job_tag': f"recurring_{interval_days}d"
            }
            
            self.scheduled_jobs.append(scheduled_job)
            logger.info(f"Scheduled recurring posts every {interval_days} days at {start_time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule recurring posts: {e}")
            return False
    
    def schedule_random_posts(self, entry_ids: List[int],
                            posts_per_week: int = 3,
                            time_windows: List[tuple] = [("09:00", "12:00"), ("15:00", "18:00")],
                            platforms: List[str] = ['twitter', 'instagram']) -> bool:
        """Schedule random posts within specified time windows"""
        try:
            def random_job():
                if self.post_callback and entry_ids:
                    # Select random entry
                    available_entries = [eid for eid in entry_ids if eid not in self.posted_content_ids]
                    if not available_entries:
                        available_entries = entry_ids  # Reset if all have been used
                        self.posted_content_ids.clear()
                    
                    entry_id = random.choice(available_entries)
                    
                    logger.info(f"Executing random post for entry {entry_id}")
                    result = self.post_callback(entry_id, platforms)
                    
                    if result:
                        self.posted_content_ids.add(entry_id)
                    
                    return result
                return False
            
            # Schedule multiple random posts per week
            days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            selected_days = random.sample(days_of_week, min(posts_per_week, 7))
            
            for day in selected_days:
                # Pick random time window
                start_time, end_time = random.choice(time_windows)
                
                # Generate random time within window
                start_hour, start_min = map(int, start_time.split(':'))
                end_hour, end_min = map(int, end_time.split(':'))
                
                random_hour = random.randint(start_hour, end_hour)
                random_min = random.randint(0, 59) if random_hour < end_hour else random.randint(0, end_min)
                
                post_time = f"{random_hour:02d}:{random_min:02d}"
                
                # Schedule the job
                getattr(schedule.every(), day).at(post_time).do(random_job).tag("random_posts")
            
            scheduled_job = {
                'type': 'random',
                'entry_ids': entry_ids,
                'posts_per_week': posts_per_week,
                'time_windows': time_windows,
                'platforms': platforms,
                'selected_days': selected_days,
                'job_tag': "random_posts"
            }
            
            self.scheduled_jobs.append(scheduled_job)
            logger.info(f"Scheduled {posts_per_week} random posts per week")
            return True
            
        except Exception as e:
            logger.error(f"Failed to schedule random posts: {e}")
            return False
    
    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        
        def run_scheduler():
            logger.info("Starting scheduler...")
            while self.running:
                try:
                    schedule.run_pending()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logger.error(f"Scheduler error: {e}")
                    time.sleep(60)
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        logger.info("Scheduler started successfully")
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def clear_all_jobs(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.scheduled_jobs.clear()
        self.posted_content_ids.clear()
        logger.info("All scheduled jobs cleared")
    
    def clear_jobs_by_tag(self, tag: str):
        """Clear jobs with specific tag"""
        schedule.clear(tag)
        self.scheduled_jobs = [job for job in self.scheduled_jobs if job.get('job_tag') != tag]
        logger.info(f"Cleared jobs with tag: {tag}")
    
    def get_next_posts(self, count: int = 5) -> List[Dict]:
        """Get information about upcoming posts"""
        upcoming = []
        
        for job in schedule.jobs:
            try:
                next_run = job.next_run
                if next_run:
                    upcoming.append({
                        'next_run': next_run,
                        'tags': list(job.tags),
                        'job_info': str(job)
                    })
            except:
                continue
        
        # Sort by next run time
        upcoming.sort(key=lambda x: x['next_run'])
        return upcoming[:count]
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            'running': self.running,
            'total_jobs': len(schedule.jobs),
            'scheduled_jobs': len(self.scheduled_jobs),
            'posted_content_count': len(self.posted_content_ids),
            'next_posts': self.get_next_posts(3)
        }
    
    def save_schedule_config(self, filepath: str):
        """Save current schedule configuration to file"""
        try:
            config = {
                'scheduled_jobs': self.scheduled_jobs,
                'posted_content_ids': list(self.posted_content_ids),
                'timestamp': datetime.now().isoformat()
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, default=str)
            
            logger.info(f"Schedule configuration saved to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to save schedule config: {e}")
            return False
    
    def load_schedule_config(self, filepath: str):
        """Load schedule configuration from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.scheduled_jobs = config.get('scheduled_jobs', [])
            self.posted_content_ids = set(config.get('posted_content_ids', []))
            
            # Recreate jobs (simplified version - you might want to enhance this)
            schedule.clear()
            
            logger.info(f"Schedule configuration loaded from {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to load schedule config: {e}")
            return False

class PostingTimeOptimizer:
    """Optimizes posting times based on platform best practices"""
    
    OPTIMAL_TIMES = {
        'twitter': {
            'weekdays': ['09:00', '12:00', '15:00', '18:00'],
            'weekends': ['10:00', '14:00', '19:00']
        },
        'instagram': {
            'weekdays': ['11:00', '13:00', '17:00', '19:00'],
            'weekends': ['10:00', '12:00', '16:00', '20:00']
        },
        'facebook': {
            'weekdays': ['09:00', '13:00', '15:00'],
            'weekends': ['12:00', '14:00', '16:00']
        },
        'linkedin': {
            'weekdays': ['08:00', '10:00', '12:00', '14:00', '17:00'],
            'weekends': []  # LinkedIn is primarily professional
        }
    }
    
    @classmethod
    def get_optimal_times(cls, platform: str, day_type: str = 'weekdays') -> List[str]:
        """Get optimal posting times for a platform"""
        return cls.OPTIMAL_TIMES.get(platform, {}).get(day_type, ['12:00'])
    
    @classmethod
    def suggest_posting_schedule(cls, platforms: List[str], posts_per_week: int = 3) -> Dict:
        """Suggest a posting schedule for multiple platforms"""
        suggestions = {}
        
        for platform in platforms:
            weekday_times = cls.get_optimal_times(platform, 'weekdays')
            weekend_times = cls.get_optimal_times(platform, 'weekends')
            
            if posts_per_week <= 3:
                # Spread across week
                suggested_times = random.sample(weekday_times, min(posts_per_week, len(weekday_times)))
            else:
                # Include weekends
                all_times = weekday_times + weekend_times
                suggested_times = random.sample(all_times, min(posts_per_week, len(all_times)))
            
            suggestions[platform] = suggested_times
        
        return suggestions

# Example usage
if __name__ == "__main__":
    # Test the scheduler
    scheduler = PostScheduler()
    
    # Example callback function
    def example_post_callback(entry_id: int, platforms: List[str]) -> bool:
        print(f"Would post entry {entry_id} to {platforms}")
        return True
    
    scheduler.set_post_callback(example_post_callback)
    
    # Test scheduling
    scheduler.schedule_recurring_posts([1, 2, 3], interval_days=1, start_time="14:00")
    
    # Get status
    status = scheduler.get_scheduler_status()
    print(f"Scheduler status: {status}")
    
    # Test time optimization
    optimizer = PostingTimeOptimizer()
    suggestions = optimizer.suggest_posting_schedule(['twitter', 'instagram'], 4)
    print(f"Posting suggestions: {suggestions}")