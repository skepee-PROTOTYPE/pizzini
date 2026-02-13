"""
Rebuild RSS feed with only valid episodes
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from google.cloud import storage
from urllib.parse import quote
import os

# Initialize Firebase Storage client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'
storage_client = storage.Client()
bucket = storage_client.bucket('pizzini-91da9')

def _sanitize_for_rss(text: str) -> str:
    import re
    s = text or ''
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    # Strip emoji ranges
    try:
        s = re.sub(r"[\U0001F300-\U0001FAFF]", "", s)
        s = re.sub(r"[\U0001F600-\U0001F64F]", "", s)
    except re.error:
        pass
    s = re.sub(r"\s+", " ", s).strip()
    return s

def list_latest_audio(limit: int = 4):
    """List latest audio blobs from podcast_audio/ in GCS."""
    blobs = bucket.list_blobs(prefix='podcast_audio/')
    episodes = []
    for b in blobs:
        if b.name.endswith('.mp3'):
            filename = b.name.split('/')[-1]
            # Title from filename prefix before _azure_ if present
            title = filename
            if '_azure_' in filename:
                title = filename.split('_azure_')[0].strip() or filename
            # Fallback generic title
            pub_dt = b.updated
            title = _sanitize_for_rss(title)
            episodes.append({
                'filename': filename,
                'size': b.size or 0,
                'date': pub_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'title': title or f"Episodio del {pub_dt.strftime('%d %b %Y')}"
            })
    # Sort by updated date descending and take top N
    episodes.sort(key=lambda e: e['date'], reverse=True)
    return episodes[:limit]

# Create RSS feed
rss = ET.Element('rss', version='2.0', attrib={
    'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'xmlns:atom': 'http://www.w3.org/2005/Atom'
})

channel = ET.SubElement(rss, 'channel')

# Add channel info
ET.SubElement(channel, 'title').text = 'I Pizzini di Don Villa'
ET.SubElement(channel, 'description').text = 'I pensieri e gli insegnamenti di Don Villa, condivisi giornalmente attraverso i suoi famosi pizzini'
ET.SubElement(channel, 'language').text = 'it'
ET.SubElement(channel, 'link').text = 'https://pizzini-b5c63.web.app'
ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'Don Villa'
ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category', text='Religion & Spirituality')

image = ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image', href='https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg')

# Add episodes (latest 4)
for ep in list_latest_audio(limit=4):
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = _sanitize_for_rss(ep['title'])
    ET.SubElement(item, 'description').text = _sanitize_for_rss(f"Episodio: {ep['title']}")
    
    # Ensure valid URL encoding for filenames (spaces and special chars)
    encoded_filename = quote(ep['filename'])
    audio_url = f"https://storage.googleapis.com/pizzini-91da9/podcast_audio/{encoded_filename}"
    ET.SubElement(item, 'enclosure', url=audio_url, type='audio/mpeg', length=str(ep['size']))
    ET.SubElement(item, 'link').text = audio_url
    ET.SubElement(item, 'guid', isPermaLink='false').text = audio_url
    ET.SubElement(item, 'pubDate').text = datetime.strptime(ep['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%a, %d %b %Y %H:%M:%S GMT')

# Pretty print XML with explicit UTF-8 encoding
xml_bytes = ET.tostring(rss, encoding='utf-8')
xml_str = minidom.parseString(xml_bytes).toprettyxml(indent='  ', encoding='utf-8')

# Save locally
with open('podcast_feed_clean.xml', 'wb') as f:
    f.write(xml_str)

# Upload to Firebase
blob = bucket.blob('podcast_feed.xml')
blob.upload_from_filename('podcast_feed_clean.xml', content_type='application/rss+xml; charset=utf-8')
blob.make_public()

print("✅ RSS feed rebuilt and uploaded!")
print(f"📡 Feed URL: https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml")
try:
    latest_eps = list_latest_audio(limit=4)
    print(f"📝 Episodes: {len(latest_eps)}")
except Exception:
    pass
