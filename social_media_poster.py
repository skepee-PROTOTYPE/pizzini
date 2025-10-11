"""
Social Media Posting Utilities
Handles posting to X (Twitter) and Instagram with proper formatting
"""

import tweepy
import instagrapi
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

class InstagramPoster:
    """Handles posting to Instagram using instagrapi"""
    
    def __init__(self, username: str, password: str):
        """Initialize Instagram client"""
        try:
            self.client = instagrapi.Client()
            self.client.login(username, password)
            logger.info("Instagram client initialized successfully")
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
    
    def __init__(self):
        self.x_poster = None
        self.instagram_poster = None
        self.image_generator = ImageGenerator()
    
    def setup_x(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        """Setup X (Twitter) posting"""
        self.x_poster = XPoster(api_key, api_secret, access_token, access_token_secret)
    
    def setup_instagram(self, username: str, password: str):
        """Setup Instagram posting"""
        self.instagram_poster = InstagramPoster(username, password)
    
    def post_to_all_platforms(self, title: str, content: str, date: str = "", 
                             include_image: bool = True) -> list:
        """Post content to all configured platforms"""
        results = []
        
        # Generate image if needed
        image_path = None
        if include_image:
            try:
                image_path = self.image_generator.create_quote_image(title, content, date)
            except Exception as e:
                logger.warning(f"Failed to generate image: {e}")
                include_image = False
        
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
            instagram_caption = f"{title}\n\n{content}\n\n#pizzini #philosophy #wisdom #italian"
            result = self.instagram_poster.post_image_with_caption(image_path, instagram_caption)
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