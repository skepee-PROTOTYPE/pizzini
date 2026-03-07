"""
Remove specific episodes from GCS and rebuild the RSS feed.
Episodes to remove (identified by their Spotify episode pages):
  - _azure_20260213_135647.mp3
  - _azure_20260213_135221.mp3
  - _azure_20260213_050015.mp3
  - Pizzini MATRIMONIO TREInfatti mamma Laura ha sorri_azure_20260213_142810.mp3
"""
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from google.cloud import storage
from urllib.parse import quote

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'
storage_client = storage.Client()
bucket = storage_client.bucket('pizzini-91da9')

# Files to delete from GCS
FILES_TO_DELETE = [
    'podcast_audio/_azure_20260213_135647.mp3',
    'podcast_audio/_azure_20260213_135221.mp3',
    'podcast_audio/_azure_20260213_050015.mp3',
    'podcast_audio/Pizzini MATRIMONIO TREInfatti mamma Laura ha sorri_azure_20260213_142810.mp3',
]

print("🗑️  Deleting unwanted episode files from Firebase Storage...")
for blob_name in FILES_TO_DELETE:
    blob = bucket.blob(blob_name)
    try:
        blob.delete()
        print(f"  ✅ Deleted: {blob_name}")
    except Exception as e:
        print(f"  ⚠️  Could not delete {blob_name}: {e}")

print()

# ---- Rebuild RSS feed (same logic as rebuild_rss.py) ----

def _sanitize_for_rss(text: str) -> str:
    import re
    s = text or ''
    s = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", " ", s)
    try:
        s = re.sub(r"[\U0001F300-\U0001FAFF]", "", s)
        s = re.sub(r"[\U0001F600-\U0001F64F]", "", s)
    except re.error:
        pass
    s = re.sub(r"\s+", " ", s).strip()
    return s


def list_latest_audio(limit: int = 10):
    """List latest valid audio blobs from podcast_audio/ in GCS."""
    blobs = bucket.list_blobs(prefix='podcast_audio/')
    episodes = []
    for b in blobs:
        if b.name.endswith('.mp3'):
            filename = b.name.split('/')[-1]
            title = filename
            if '_azure_' in filename:
                title = filename.split('_azure_')[0].strip() or filename
            pub_dt = b.updated
            title = _sanitize_for_rss(title)
            episodes.append({
                'filename': filename,
                'size': b.size or 0,
                'date': pub_dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'title': title or f"Episodio del {pub_dt.strftime('%d %b %Y')}"
            })
    episodes.sort(key=lambda e: e['date'], reverse=True)
    return episodes[:limit]


print("🔨 Rebuilding RSS feed...")
episodes = list_latest_audio(limit=10)
print(f"  Found {len(episodes)} episode(s) remaining in storage.")
for ep in episodes:
    print(f"    - {ep['title']} ({ep['date']})")

# Build RSS
rss = ET.Element('rss', version='2.0', attrib={
    'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'xmlns:atom': 'http://www.w3.org/2005/Atom'
})
channel = ET.SubElement(rss, 'channel')
ET.SubElement(channel, 'title').text = 'I Pizzini di Don Villa'
ET.SubElement(channel, 'description').text = (
    'I pensieri e gli insegnamenti di Don Villa, condivisi giornalmente attraverso i suoi famosi pizzini'
)
ET.SubElement(channel, 'language').text = 'it'
ET.SubElement(channel, 'link').text = 'https://pizzini-b5c63.web.app'
ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text = 'Don Villa'
ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}category',
              text='Religion & Spirituality')
ET.SubElement(channel, '{http://www.itunes.com/dtds/podcast-1.0.dtd}image',
              href='https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg')

for ep in episodes:
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = _sanitize_for_rss(ep['title'])
    ET.SubElement(item, 'description').text = _sanitize_for_rss(f"Episodio: {ep['title']}")
    encoded_filename = quote(ep['filename'])
    audio_url = f"https://storage.googleapis.com/pizzini-91da9/podcast_audio/{encoded_filename}"
    ET.SubElement(item, 'enclosure', url=audio_url, type='audio/mpeg', length=str(ep['size']))
    ET.SubElement(item, 'link').text = audio_url
    ET.SubElement(item, 'guid', isPermaLink='false').text = audio_url
    ET.SubElement(item, 'pubDate').text = (
        datetime.strptime(ep['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%a, %d %b %Y %H:%M:%S GMT')
    )

xml_bytes = ET.tostring(rss, encoding='utf-8')
xml_str = minidom.parseString(xml_bytes).toprettyxml(indent='  ', encoding='utf-8')

with open('podcast_feed_clean.xml', 'wb') as f:
    f.write(xml_str)
print("  ✅ Local podcast_feed_clean.xml updated.")

# Upload to Firebase Storage
print()
print("📤 Uploading new feed to Firebase Storage...")
blob = bucket.blob('podcast_feed.xml')
blob.upload_from_filename('podcast_feed_clean.xml', content_type='application/rss+xml; charset=utf-8')
blob.make_public()
print("  ✅ Uploaded as podcast_feed.xml")
print()
print(f"📡 Feed URL: https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml")
print()
print("✅ Done! Spotify will sync the updated feed within 24–72 hours.")
print("   If you need immediate removal, also unpublish manually at:")
print("   https://podcasters.spotify.com/")
