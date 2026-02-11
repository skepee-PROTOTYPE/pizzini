"""
AI Agent for intelligent podcast and Facebook publishing decisions.
Uses Google Gemini 1.5 Flash (free tier) for decision-making.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)

# Lazy import for Gemini (only load when needed)
GEMINI_AVAILABLE = True

class PublishingAgent:
    """AI agent that decides when and what to post based on context and learning."""
    
    def __init__(self, config: Dict, db, storage_bucket):
        """
        Initialize the AI agent.
        
        Args:
            config: Configuration dictionary from Firestore
            db: Firestore client
            storage_bucket: Firebase Storage bucket
        """
        self.config = config
        self.db = db
        self.storage_bucket = storage_bucket
        self.model = None
        
    def _init_gemini(self):
        """Lazy initialization of Gemini model."""
        if self.model is not None:
            return
            
        try:
            import google.generativeai as genai
            
            api_key = self.config.get('ai_agent', {}).get('gemini_api_key')
            if not api_key:
                logger.error("Gemini API key not found in config")
                return
                
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            logger.info("Gemini model initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {e}")
            
    def should_post_now(self) -> Tuple[bool, str]:
        """
        Decide if we should post now based on multiple factors.
        
        Returns:
            Tuple of (should_post: bool, reason: str)
        """
        try:
            # Get last posting time
            last_post_time = self._get_last_post_time()
            hours_since_last = (datetime.now() - last_post_time).total_seconds() / 3600
            
            # Get current hour (Rome timezone aware)
            current_hour = datetime.now().hour
            
            # Get recent engagement metrics
            avg_engagement = self._get_average_engagement()
            
            # Get historical best posting times
            best_hours = self._get_best_posting_hours()
            
            # Initialize Gemini
            self._init_gemini()
            
            if self.model is None:
                # Fallback to rule-based logic if AI unavailable
                return self._rule_based_decision(hours_since_last, current_hour)
            
            # Build context for AI
            prompt = f"""You are an AI agent managing a Facebook page and podcast about Italian religious traditions.

CURRENT SITUATION:
- Current time: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p')}
- Current hour: {current_hour}:00
- Hours since last post: {hours_since_last:.1f}
- Average engagement per post: {avg_engagement:.0f} interactions
- Historically best posting hours: {best_hours}

POSTING RULES:
1. Post at least once every 24-26 hours (daily frequency)
2. Best engagement happens between 7-9 AM Italian time
3. Avoid posting at night (after 10 PM or before 6 AM)
4. Weekday mornings (7-8 AM) typically get better engagement than weekends

DECISION NEEDED:
Should I post now or wait?

Respond ONLY with valid JSON (no markdown, no code blocks):
{{"should_post": true or false, "reason": "brief explanation", "confidence": 0-100}}

Examples:
{{"should_post": true, "reason": "24 hours since last post and currently in peak engagement window (7-9 AM)", "confidence": 95}}
{{"should_post": false, "reason": "Only 6 hours since last post, too soon", "confidence": 90}}
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response if it has markdown code blocks
            if response_text.startswith('```'):
                # Extract JSON from markdown code block
                lines = response_text.split('\n')
                json_lines = [l for l in lines if not l.startswith('```')]
                response_text = '\n'.join(json_lines).strip()
            
            decision = json.loads(response_text)
            
            should_post = decision.get('should_post', False)
            reason = decision.get('reason', 'AI decision')
            confidence = decision.get('confidence', 50)
            
            logger.info(f"AI Decision: should_post={should_post}, reason={reason}, confidence={confidence}%")
            
            # Log decision to Firestore for learning
            self._log_decision(should_post, reason, confidence)
            
            return should_post, reason
            
        except Exception as e:
            logger.error(f"Error in should_post_now: {e}")
            # Fallback to simple rule-based
            if hours_since_last >= 23:
                return True, f"Fallback: {hours_since_last:.0f}h since last post"
            return False, f"Fallback: Only {hours_since_last:.0f}h since last post"
    
    def select_episode(self, available_episodes: List[Dict]) -> Optional[Dict]:
        """
        Select the best episode to post based on AI analysis.
        
        Args:
            available_episodes: List of episode dictionaries with title, description, guid
            
        Returns:
            Selected episode dict or None
        """
        if not available_episodes:
            logger.warning("No available episodes to select from")
            return None
            
        try:
            self._init_gemini()
            
            if self.model is None:
                # Fallback: return first unposted episode
                return self._get_next_sequential_episode(available_episodes)
            
            # Get recently posted episodes to avoid repetition
            recent_posts = self._get_recent_posts(limit=5)
            recent_themes = [p.get('theme', '') for p in recent_posts]
            
            # Build episode list for AI
            episode_info = []
            for i, ep in enumerate(available_episodes[:10]):  # Limit to 10 for API token limits
                episode_info.append(f"{i+1}. Title: {ep.get('title', 'Untitled')}\n   Description: {ep.get('description', 'No description')[:200]}")
            
            current_date = datetime.now()
            
            prompt = f"""You are selecting the best episode to post today for an Italian religious traditions podcast.

CURRENT CONTEXT:
- Date: {current_date.strftime('%B %d, %Y')}
- Day: {current_date.strftime('%A')}
- Upcoming holidays: {self._get_upcoming_holidays(current_date)}

RECENTLY POSTED THEMES (avoid repeating):
{', '.join(recent_themes) if recent_themes else 'None'}

AVAILABLE EPISODES:
{chr(10).join(episode_info)}

SELECTION CRITERIA:
1. Topical relevance (match to current date, upcoming holidays)
2. Theme variety (don't repeat recent themes)
3. Seasonal appropriateness
4. Audience interest patterns

Which episode should I post? 

Respond ONLY with valid JSON (no markdown, no code blocks):
{{"episode_number": 1-10, "reason": "brief explanation", "confidence": 0-100}}

Example:
{{"episode_number": 3, "reason": "Valentine's Day is in 3 days, this episode about love and devotion is perfectly timed", "confidence": 90}}
"""
            
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith('```'):
                lines = response_text.split('\n')
                json_lines = [l for l in lines if not l.startswith('```')]
                response_text = '\n'.join(json_lines).strip()
            
            selection = json.loads(response_text)
            
            episode_num = selection.get('episode_number', 1)
            reason = selection.get('reason', 'AI selection')
            
            if 1 <= episode_num <= len(available_episodes):
                selected = available_episodes[episode_num - 1]
                logger.info(f"AI selected episode {episode_num}: {selected.get('title')} - {reason}")
                
                # Log selection for learning
                self._log_episode_selection(selected, reason)
                
                return selected
            else:
                logger.warning(f"AI selected invalid episode number: {episode_num}")
                return available_episodes[0]
                
        except Exception as e:
            logger.error(f"Error in select_episode: {e}")
            return self._get_next_sequential_episode(available_episodes)
    
    def validate_post_success(self, fb_post_id: Optional[str], podcast_url: Optional[str]) -> Dict:
        """
        Validate that posting was successful and log results.
        
        Returns:
            Dict with validation results and any issues found
        """
        issues = []
        
        # Check Facebook post
        if not fb_post_id:
            issues.append("Facebook post failed - no post ID")
        
        # Check podcast
        if not podcast_url:
            issues.append("Podcast upload failed - no URL")
        elif not self._verify_audio_accessible(podcast_url):
            issues.append("Podcast URL not accessible")
        
        # Check RSS feed
        rss_valid, rss_issues = self._validate_rss_feed()
        if not rss_valid:
            issues.extend(rss_issues)
        
        success = len(issues) == 0
        
        # Log validation results
        self._log_validation({
            'success': success,
            'fb_post_id': fb_post_id,
            'podcast_url': podcast_url,
            'issues': issues,
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'success': success,
            'issues': issues,
            'auto_fixed': []
        }
    
    # Helper methods
    
    def _get_last_post_time(self) -> datetime:
        """Get timestamp of last successful post."""
        try:
            posts_ref = self.db.collection('posting_activity').order_by('timestamp', direction='DESCENDING').limit(1)
            posts = list(posts_ref.stream())
            
            if posts:
                last_post = posts[0].to_dict()
                return datetime.fromisoformat(last_post['timestamp'].replace('Z', '+00:00'))
            else:
                # No posts yet, return 24 hours ago
                return datetime.now() - timedelta(hours=24)
                
        except Exception as e:
            logger.error(f"Error getting last post time: {e}")
            return datetime.now() - timedelta(hours=24)
    
    def _get_average_engagement(self) -> float:
        """Calculate average engagement from recent posts."""
        try:
            posts_ref = self.db.collection('posting_activity').order_by('timestamp', direction='DESCENDING').limit(10)
            posts = [p.to_dict() for p in posts_ref.stream()]
            
            if not posts:
                return 45.0  # Default baseline
            
            total_engagement = sum(p.get('engagement', 0) for p in posts)
            return total_engagement / len(posts)
            
        except Exception as e:
            logger.error(f"Error calculating engagement: {e}")
            return 45.0
    
    def _get_best_posting_hours(self) -> List[int]:
        """Analyze historical data to find best posting hours."""
        # For now, return default best hours based on social media research
        # TODO: Implement actual historical analysis
        return [7, 8, 9]  # 7-9 AM typically best
    
    def _rule_based_decision(self, hours_since_last: float, current_hour: int) -> Tuple[bool, str]:
        """Fallback rule-based decision if AI unavailable."""
        # Post if it's been 23+ hours and we're in reasonable hours (6 AM - 10 PM)
        if hours_since_last >= 23 and 6 <= current_hour <= 22:
            return True, f"Rule: {hours_since_last:.0f}h since last post, within posting window"
        elif hours_since_last >= 26:
            return True, f"Rule: {hours_since_last:.0f}h since last post, overdue"
        else:
            return False, f"Rule: Only {hours_since_last:.0f}h since last post"
    
    def _get_next_sequential_episode(self, available_episodes: List[Dict]) -> Optional[Dict]:
        """Fallback: select next unposted episode sequentially."""
        if available_episodes:
            return available_episodes[0]
        return None
    
    def _get_recent_posts(self, limit: int = 5) -> List[Dict]:
        """Get recent posts for context."""
        try:
            posts_ref = self.db.collection('posting_activity').order_by('timestamp', direction='DESCENDING').limit(limit)
            return [p.to_dict() for p in posts_ref.stream()]
        except Exception as e:
            logger.error(f"Error getting recent posts: {e}")
            return []
    
    def _get_upcoming_holidays(self, current_date: datetime) -> str:
        """Get upcoming Italian/Catholic holidays for context."""
        # Simple holiday lookup (could be expanded)
        holidays = {
            (2, 14): "Valentine's Day",
            (3, 19): "St. Joseph's Day",
            (4, 20): "Easter (varies)",
            (5, 1): "May Day",
            (8, 15): "Assumption of Mary",
            (11, 1): "All Saints' Day",
            (12, 8): "Immaculate Conception",
            (12, 25): "Christmas"
        }
        
        upcoming = []
        for days_ahead in range(1, 15):  # Look 2 weeks ahead
            future_date = current_date + timedelta(days=days_ahead)
            key = (future_date.month, future_date.day)
            if key in holidays:
                upcoming.append(f"{holidays[key]} in {days_ahead} days")
        
        return ', '.join(upcoming) if upcoming else "None in next 2 weeks"
    
    def _verify_audio_accessible(self, url: str) -> bool:
        """Check if audio file is accessible."""
        try:
            # Extract filename from URL and check in Storage
            if 'podcast_audio/' in url:
                filename = url.split('podcast_audio/')[-1].split('?')[0]
                blob = self.storage_bucket.blob(f'podcast_audio/{filename}')
                return blob.exists()
            return False
        except Exception as e:
            logger.error(f"Error verifying audio: {e}")
            return False
    
    def _validate_rss_feed(self) -> Tuple[bool, List[str]]:
        """Validate RSS feed structure and content."""
        issues = []
        
        try:
            # Download RSS feed
            blob = self.storage_bucket.blob('podcast_feed.xml')
            if not blob.exists():
                return False, ["RSS feed not found"]
            
            rss_content = blob.download_as_text()
            root = ET.fromstring(rss_content)
            
            # Find all items
            items = root.findall('.//item')
            
            if len(items) == 0:
                issues.append("RSS feed has no episodes")
            
            # Check each item
            for item in items:
                enclosure = item.find('enclosure')
                if enclosure is not None:
                    file_size = enclosure.get('length', '0')
                    if file_size == '1' or int(file_size) < 100000:  # Less than 100KB is suspicious
                        issues.append(f"Episode has invalid file size: {file_size}")
                    
                    url = enclosure.get('url', '')
                    if 'placeholder' in url.lower() or not url.startswith('http'):
                        issues.append(f"Episode has invalid URL: {url}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            logger.error(f"Error validating RSS: {e}")
            return False, [f"RSS validation error: {str(e)}"]
    
    def _log_decision(self, should_post: bool, reason: str, confidence: int):
        """Log AI decision to Firestore for learning."""
        try:
            self.db.collection('ai_decisions').add({
                'timestamp': datetime.now().isoformat(),
                'decision': 'post' if should_post else 'wait',
                'reason': reason,
                'confidence': confidence,
                'type': 'posting_decision'
            })
        except Exception as e:
            logger.error(f"Error logging decision: {e}")
    
    def _log_episode_selection(self, episode: Dict, reason: str):
        """Log episode selection for learning."""
        try:
            self.db.collection('ai_decisions').add({
                'timestamp': datetime.now().isoformat(),
                'episode_title': episode.get('title'),
                'episode_guid': episode.get('guid'),
                'reason': reason,
                'type': 'episode_selection'
            })
        except Exception as e:
            logger.error(f"Error logging selection: {e}")
    
    def _log_validation(self, results: Dict):
        """Log validation results."""
        try:
            self.db.collection('validation_logs').add(results)
        except Exception as e:
            logger.error(f"Error logging validation: {e}")
