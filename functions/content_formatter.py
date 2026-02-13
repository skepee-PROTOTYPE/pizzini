"""
Content Formatter for Social Media
Formats Italian pizzini content for different social media platforms
"""

import re
import hashlib
from typing import List, Dict, Tuple
from datetime import datetime

class ContentFormatter:
    """Formats content for various social media platforms"""
    
    # Platform-specific limits
    PLATFORM_LIMITS = {
        'twitter': {'text': 280, 'hashtags': 2},
        'x': {'text': 280, 'hashtags': 2},
        'instagram': {'text': 2200, 'hashtags': 30},
        'facebook': {'text': 63206, 'hashtags': 3},
        'linkedin': {'text': 3000, 'hashtags': 3}
    }
    
    # Italian-themed hashtags for pizzini content
    ITALIAN_HASHTAGS = [
        '#saggezza', '#filosofia', '#riflessioni', '#pensieri', 
        '#vita', '#crescita', '#ispirazione', '#meditazione',
        '#pizzini', '#italian', '#wisdom', '#philosophy',
        '#thoughts', '#life', '#inspiration', '#reflection'
    ]

    # Fixed Instagram hashtag set (used for every IG post, truncated to platform limit)
    INSTAGRAM_FIXED_HASHTAGS = [
        '#pizzini', '#filosofia', '#saggezza', '#riflessioni', '#pensieri',
        '#ispirazione', '#meditazione', '#vita', '#crescita', '#italia',
        '#italianquotes', '#philosophy', '#wisdom', '#mindset', '#reflection',
        '#thoughts', '#innergrowth', '#dailywisdom', '#quoteoftheday', '#italianlife'
    ]
    
    # Platform-specific emoji sets
    PLATFORM_EMOJIS = {
        'twitter': ['🤔', '💭', '📝', '✨', '🇮🇹'],
        'instagram': ['🤔', '💭', '📝', '✨', '🇮🇹', '📖', '🌟', '💡'],
        'facebook': ['🤔', '💭', '📝'],
        'linkedin': ['💭', '📝', '✨']
    }
    
    def __init__(self):
        self.used_hashtags = set()  # Track used hashtags to avoid repetition

    # Basic female names used to choose Santa vs San
    FEMALE_NAMES = {
        'maria','teresa','lucia','anna','cecilia','elisabetta','caterina','rita','chiara','giuseppina','paola'
    }

    # Common English→Italian saint names
    EN_TO_IT_SAINTS = {
        'peter': 'pietro',
        'paul': 'paolo',
        'john': 'giovanni',
        'anthony': 'antonio',
        'stephen': 'stefano',
        'mary': 'maria',
        'teresa': 'teresa',
        'mark': 'marco',
        'luke': 'luca'
    }
    
    def format_for_platform(self, title: str, content: str, platform: str, 
                           date: str = "", include_hashtags: bool = True) -> Dict[str, str]:
        """Format content for a specific platform"""
        platform = platform.lower()
        limits = self.PLATFORM_LIMITS.get(platform, self.PLATFORM_LIMITS['twitter'])

        # Sanitize text to avoid TTS oddities and social artefacts
        safe_content = self.sanitize_for_social(content)
        formatted_post = self._create_base_post(title, safe_content, platform, limits)
        
        if include_hashtags:
            hashtags = self._select_hashtags(content, platform, limits['hashtags'])
            formatted_post = self._add_hashtags(formatted_post, hashtags, limits['text'])
        
        # Add platform-specific formatting
        if platform in ['instagram']:
            formatted_post = self._add_instagram_formatting(formatted_post, date)
        elif platform in ['twitter', 'x']:
            formatted_post = self._add_twitter_formatting(formatted_post, date)
        elif platform == 'linkedin':
            formatted_post = self._add_linkedin_formatting(formatted_post, title)
        
        return {
            'text': formatted_post,
            'length': len(formatted_post),
            'platform': platform,
            'within_limits': len(formatted_post) <= limits['text']
        }

    def sanitize_for_social(self, content: str) -> str:
        """Sanitize text for social posts (normalize punctuation/quotes/entities)."""
        text = content or ""
        # Normalize whitespace
        text = re.sub(r"\s+", " ", text.strip())
        # Replace XML/HTML entities
        text = (text
                .replace('&amp;', '&')
                .replace('&quot;', '"')
                .replace('&apos;', "'")
                .replace('&lt;', '<')
                .replace('&gt;', '>'))
        # Normalize quotes
        text = (text
                .replace('“', '"').replace('”', '"')
                .replace('‘', "'").replace('’', "'"))
        # Remove stray tags
        text = re.sub(r'<[^>]+>', '', text)
        # Fix spacing around punctuation
        text = re.sub(r'\s*([.!?,;:])\s*', r'\1 ', text)
        return text.strip()

    def sanitize_for_tts(self, content: str) -> str:
        """Sanitize text specifically for Italian TTS.
        - Expand abbreviations like 'S.' → 'San/Santa'
        - Map 'St.'/'Saint' with English names to Italian (e.g., 'St. Peter' → 'San Pietro')
        - Normalize punctuation to avoid spoken 'punto' from abbreviations
        """
        text = self.sanitize_for_social(content)

        # SS. Trinità → Santissima Trinità
        text = re.sub(r'\bSS\.?\s+Trinità\b', 'Santissima Trinità', text, flags=re.IGNORECASE)
        # S. Messa → Santa Messa
        text = re.sub(r'\bS\.?\s+Messa\b', 'Santa Messa', text, flags=re.IGNORECASE)

        # Expand S. <Name> → San/Santa <Name>
        def _expand_s_abbrev(m):
            name = m.group(1)
            base = name.lower()
            title = 'Santa' if base in self.FEMALE_NAMES else 'San'
            # Preserve original capitalization of name
            return f"{title} {name}"
        text = re.sub(r'\bS\.?\s+([A-ZÀ-Ü][a-zà-ü]+)\b', _expand_s_abbrev, text)

        # Handle English saint forms: St. / Saint <Name>
        def _expand_st_english(m):
            raw = m.group(1)
            base = raw.lower()
            it = self.EN_TO_IT_SAINTS.get(base, raw)
            title = 'Santa' if base in self.FEMALE_NAMES else 'San'
            return f"{title} {it.capitalize()}"
        text = re.sub(r'\bSt\.?\s+([A-Z][a-z]+)\b', _expand_st_english, text)
        text = re.sub(r'\bSaint\s+([A-Z][a-z]+)\b', _expand_st_english, text)

        # Avoid single-letter abbreviations followed by dot at line end causing 'punto' spoken
        # Replace isolated " ." or trailing " ." with just a pause
        text = re.sub(r'\s*\.$', '.', text)
        return text.strip()
    
    def _create_base_post(self, title: str, content: str, platform: str, limits: Dict) -> str:
        """Create the base post content"""
        # Clean and prepare content
        cleaned_content = self._clean_content(content)
        
        if platform == 'instagram':
            # Instagram allows longer content
            post = f"{title}\n\n{cleaned_content}"
        elif platform in ['twitter', 'x']:
            # Twitter/X has strict limits
            available_chars = limits['text'] - 50  # Reserve space for hashtags
            post = self._create_twitter_post(title, cleaned_content, available_chars)
        elif platform == 'linkedin':
            # LinkedIn professional format
            post = f"{title}\n\n{cleaned_content}"
        else:
            # Default format
            post = f"{title}\n\n{cleaned_content}"
        
        return post
    
    def _create_twitter_post(self, title: str, content: str, max_chars: int) -> str:
        """Create a Twitter-optimized post"""
        # Start with title
        post = title
        
        # Add content if there's space
        remaining_chars = max_chars - len(post)
        
        if remaining_chars > 20:  # Need space for ellipsis and formatting
            post += "\n\n"
            content_space = remaining_chars - 2
            
            if len(content) <= content_space:
                post += content
            else:
                # Find a good breaking point
                truncated = content[:content_space - 3]
                last_period = truncated.rfind('.')
                last_space = truncated.rfind(' ')
                
                if last_period > len(truncated) * 0.8:
                    post += content[:last_period + 1]
                elif last_space > len(truncated) * 0.8:
                    post += content[:last_space] + "..."
                else:
                    post += truncated + "..."
        
        return post
    
    def _clean_content(self, content: str) -> str:
        """Clean and prepare content for social media"""
        return self.sanitize_for_social(content)
    
    def _select_hashtags(self, content: str, platform: str, max_count: int) -> List[str]:
        """Select appropriate hashtags based on content and platform"""
        if platform == 'instagram':
            return self.INSTAGRAM_FIXED_HASHTAGS[:max_count]

        selected_hashtags = []
        
        # Content-based hashtag selection
        content_lower = content.lower()
        
        # Always include basic ones for pizzini content
        if '#pizzini' not in self.used_hashtags:
            selected_hashtags.append('#pizzini')
            self.used_hashtags.add('#pizzini')
        
        # Add content-specific hashtags
        keyword_hashtags = {
            'rapporto': '#relazioni',
            'infinito': '#infinito',
            'libertà': '#libertà',
            'amico': '#amicizia',
            'fidarsi': '#fiducia',
            'pensiero': '#pensieri',
            'vita': '#vita',
            'aiuto': '#aiuto'
        }
        
        for keyword, hashtag in keyword_hashtags.items():
            if keyword in content_lower and len(selected_hashtags) < max_count:
                if hashtag not in self.used_hashtags:
                    selected_hashtags.append(hashtag)
                    self.used_hashtags.add(hashtag)
        
        # Fill remaining slots with general hashtags
        available_general = [h for h in self.ITALIAN_HASHTAGS if h not in self.used_hashtags]
        
        while len(selected_hashtags) < max_count and available_general:
            hashtag = available_general.pop(0)
            selected_hashtags.append(hashtag)
            self.used_hashtags.add(hashtag)
        
        return selected_hashtags[:max_count]
    
    def _add_hashtags(self, post: str, hashtags: List[str], char_limit: int) -> str:
        """Add hashtags to post if they fit"""
        if not hashtags:
            return post
        
        hashtag_string = " " + " ".join(hashtags)
        
        if len(post + hashtag_string) <= char_limit:
            return post + hashtag_string
        else:
            # Try to fit as many hashtags as possible
            fitted_hashtags = []
            for hashtag in hashtags:
                test_string = post + " " + " ".join(fitted_hashtags + [hashtag])
                if len(test_string) <= char_limit:
                    fitted_hashtags.append(hashtag)
                else:
                    break
            
            if fitted_hashtags:
                return post + " " + " ".join(fitted_hashtags)
            else:
                return post
    
    def _add_instagram_formatting(self, post: str, date: str) -> str:
        """Add Instagram-specific formatting"""
        if date:
            post += f"\n\n📅 {date}"
        
        # Add line breaks for readability
        post = post.replace('. ', '.\n\n')
        
        return post
    
    def _add_twitter_formatting(self, post: str, date: str) -> str:
        """Add Twitter-specific formatting"""
        # Twitter formatting is minimal due to character limits
        return post
    
    def _add_linkedin_formatting(self, post: str, title: str) -> str:
        """Add LinkedIn professional formatting"""
        # LinkedIn appreciates professional formatting
        # Guard against empty title: replacing "" inserts between every character
        safe_title = (title or "").strip()
        if safe_title:
            # Only replace first occurrence (the heading)
            return post.replace(safe_title, f"💭 {safe_title}", 1)
        # No title available: just prefix the post
        return f"💭 {post}"
    
    def create_thread(self, title: str, content: str, platform: str = 'twitter') -> List[str]:
        """Create a thread for long content"""
        if platform not in ['twitter', 'x']:
            return [self.format_for_platform(title, content, platform)['text']]
        
        limit = self.PLATFORM_LIMITS[platform]['text'] - 20  # Reserve space for thread numbering
        
        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        threads = []
        current_thread = title + "\n\n"
        thread_count = 1
        
        for sentence in sentences:
            test_thread = current_thread + sentence + ". "
            
            if len(test_thread) > limit:
                # Finish current thread
                threads.append(f"{current_thread} ({thread_count}/{thread_count + len(sentences) - sentences.index(sentence)})")
                thread_count += 1
                current_thread = sentence + ". "
            else:
                current_thread = test_thread
        
        # Add the last thread
        if current_thread.strip():
            threads.append(f"{current_thread} ({thread_count}/{thread_count})")
        
        return threads
    
    def get_optimal_posting_time(self, platform: str) -> str:
        """Get optimal posting times for different platforms"""
        times = {
            'twitter': "9:00-10:00 AM, 7:00-9:00 PM",
            'x': "9:00-10:00 AM, 7:00-9:00 PM", 
            'instagram': "11:00 AM-1:00 PM, 7:00-9:00 PM",
            'facebook': "1:00-3:00 PM, 7:00-9:00 PM",
            'linkedin': "8:00-10:00 AM, 12:00-2:00 PM"
        }
        return times.get(platform.lower(), "9:00 AM-12:00 PM")

# Example usage and testing
if __name__ == "__main__":
    formatter = ContentFormatter()
    
    # Test with sample pizzini content
    title = "AIUTO PER IL PIZZINO (1°)"
    content = ("La parola rapporto dice che una cosa c'entra con un'altra. "
               "Tu potresti fare un lunghissimo elenco di cose in rapporto e scopriresti subito che c'è una legge importantissima...")
    
    # Test formatting for different platforms
    platforms = ['twitter', 'instagram', 'facebook', 'linkedin']
    
    for platform in platforms:
        result = formatter.format_for_platform(title, content, platform, "17.09.2012")
        print(f"\n=== {platform.upper()} ===")
        print(f"Length: {result['length']}/{formatter.PLATFORM_LIMITS[platform]['text']}")
        print(f"Within limits: {result['within_limits']}")
        print(f"Content:\n{result['text']}")
        print("-" * 50)