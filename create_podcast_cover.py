"""Create podcast cover art for I Pizzini di Don Villa"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_podcast_cover():
    """Create 3000x3000 podcast cover art (Spotify requirement)"""
    
    # Create image (3000x3000 minimum for Spotify)
    width, height = 3000, 3000
    
    # Colors - Italian religious theme
    bg_color = (245, 240, 230)  # Warm cream
    text_color = (80, 50, 30)   # Dark brown
    accent_color = (150, 100, 50)  # Gold/brown
    
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw decorative border
    border_width = 100
    draw.rectangle(
        [(border_width, border_width), (width - border_width, height - border_width)],
        outline=accent_color,
        width=20
    )
    
    # Try to load font (fallback to default if not available)
    try:
        title_font = ImageFont.truetype("arial.ttf", 280)
        subtitle_font = ImageFont.truetype("arial.ttf", 180)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Draw title
    title = "I PIZZINI"
    subtitle = "di Don Villa"
    
    # Center text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 2 - 300
    
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = height // 2 + 100
    
    # Draw text with shadow
    shadow_offset = 8
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, fill=(200, 180, 160), font=title_font)
    draw.text((title_x, title_y), title, fill=text_color, font=title_font)
    
    draw.text((subtitle_x + shadow_offset, subtitle_y + shadow_offset), subtitle, fill=(200, 180, 160), font=subtitle_font)
    draw.text((subtitle_x, subtitle_y), subtitle, fill=accent_color, font=subtitle_font)
    
    # Add tagline at bottom
    tagline = "Pensieri Spirituali Quotidiani"
    try:
        tagline_font = ImageFont.truetype("arial.ttf", 100)
    except:
        tagline_font = ImageFont.load_default()
    
    tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tagline_width = tagline_bbox[2] - tagline_bbox[0]
    tagline_x = (width - tagline_width) // 2
    tagline_y = height - 400
    
    draw.text((tagline_x, tagline_y), tagline, fill=accent_color, font=tagline_font)
    
    # Save
    output_path = 'podcast_cover.jpg'
    img.save(output_path, 'JPEG', quality=95)
    print(f"✅ Podcast cover created: {output_path}")
    print(f"📐 Size: {width}x{height} (meets Spotify requirements)")
    
    return output_path

if __name__ == '__main__':
    create_podcast_cover()
