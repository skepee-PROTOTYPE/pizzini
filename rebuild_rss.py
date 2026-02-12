"""
Rebuild RSS feed with only valid episodes
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime
from google.cloud import storage
import os

# Initialize Firebase Storage client
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'serviceAccountKey.json'
storage_client = storage.Client()
bucket = storage_client.bucket('pizzini-91da9')

# Valid episodes (from gsutil ls output)
valid_episodes = [
    {
        'filename': '_azure_20260211_152040.mp3',
        'size': 3269510,
        'date': '2026-02-11T15:20:43Z',
        'title': 'FESTA DELLA SANTISSIMA TRINITÀ'
    },
    {
        'filename': '_azure_20260211_151148.mp3', 
        'size': 2618018,
        'date': '2026-02-11T15:11:51Z',
        'title': 'Episodio del 11 Febbraio 2026'
    },
    {
        'filename': 'AIUTO PER IL PIZZINO 1_azure_20260209_153137.mp3',
        'size': 4246004,
        'date': '2026-02-09T17:21:53Z',
        'title': 'AIUTO PER IL PIZZINO 1'
    }
]

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

# Add episodes
for ep in valid_episodes:
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = ep['title']
    ET.SubElement(item, 'description').text = f"Episodio: {ep['title']}"
    
    audio_url = f"https://storage.googleapis.com/pizzini-91da9/podcast_audio/{ep['filename']}"
    ET.SubElement(item, 'enclosure', url=audio_url, type='audio/mpeg', length=str(ep['size']))
    ET.SubElement(item, 'link').text = audio_url
    ET.SubElement(item, 'guid', isPermaLink='false').text = audio_url
    ET.SubElement(item, 'pubDate').text = datetime.strptime(ep['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%a, %d %b %Y %H:%M:%S GMT')

# Pretty print XML
xml_str = minidom.parseString(ET.tostring(rss)).toprettyxml(indent='  ')

# Save locally
with open('podcast_feed_clean.xml', 'w', encoding='utf-8') as f:
    f.write(xml_str)

# Upload to Firebase
blob = bucket.blob('podcast_feed.xml')
blob.upload_from_filename('podcast_feed_clean.xml', content_type='application/rss+xml')
blob.make_public()

print("✅ RSS feed rebuilt and uploaded!")
print(f"📡 Feed URL: https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml")
print(f"📝 Episodes: {len(valid_episodes)}")
