"""Rebuild the podcast RSS feed from all audio files in Firebase Storage."""
import firebase_admin, json, re, os
from firebase_admin import credentials, storage
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from xml.dom import minidom

with open('serviceAccountKey.json', encoding='utf-8') as f:
    sa = json.load(f)
project_id = sa['project_id']

with open('config.json', encoding='utf-8') as f:
    cfg = json.load(f)
podcast_cfg = cfg.get('podcast_info', cfg.get('podcast', {}))

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    firebase_admin.initialize_app(cred, {'storageBucket': project_id})

bucket = storage.bucket()
blobs = list(bucket.list_blobs(prefix='podcast_audio/'))

# Corrections for titles whose filenames lost apostrophes or accents
TITLE_CORRECTIONS = {
    'LUOMO NASCE RELIGIOSUS': "L'uomo nasce religiosus",
    'LAMICO':                 "L'AMICO",
    'STUPIDITA':              'STUPIDITÀ',
    'VERITA DUE':             'VERITÀ DUE',
    'LIBERTA':                'LIBERTÀ',
    'UNIVERSITA':             'UNIVERSITÀ',
    'CIVILTA':                'CIVILTÀ',
    'PATERNITA':              'PATERNITÀ',
    'MATERNITA':              'MATERNITÀ',
    'VOLONTA':                'VOLONTÀ',
    'VERITA':                 'VERITÀ',
    'CARITA':                 'CARITÀ',
    'UMILTA':                 'UMILTÀ',
    'REALTA':                 'REALTÀ',
    'IDENTITA':               'IDENTITÀ',
    'AUTORITA':               'AUTORITÀ',
    'QUALITA':                'QUALITÀ',
}

# Parse each blob: TITLE_azure|cloudtts_YYYYMMDD_HHMMSS.mp3
episodes = {}
for b in blobs:
    name = os.path.basename(b.name)
    m = re.match(r'^(.+?)_(azure|cloudtts)_(\d{8}_\d{6})\.mp3$', name)
    if not m:
        continue
    raw_title = m.group(1).strip()
    svc       = m.group(2)
    ts        = m.group(3)
    if not raw_title:
        continue
    dt = datetime.strptime(ts, '%Y%m%d_%H%M%S')
    key = raw_title.upper().strip()
    existing = episodes.get(key)
    # Prefer cloudtts; otherwise keep newest
    if existing is None:
        take = True
    elif svc == 'cloudtts' and existing['svc'] != 'cloudtts':
        take = True
    elif svc != 'cloudtts' and existing['svc'] == 'cloudtts':
        take = False
    else:
        take = dt > existing['dt']
    if take:
        corrected_title = TITLE_CORRECTIONS.get(key, raw_title)
        episodes[key] = {
            'title': corrected_title,
            'dt': dt,
            'url': b.public_url,
            'size': b.size,
            'svc': svc,
        }

# Sort newest first
eps = sorted(episodes.values(), key=lambda e: e['dt'], reverse=True)
print(f'Building RSS with {len(eps)} episodes:')
for e in eps:
    print(f"  {e['title']} | {e['dt'].strftime('%d %b %Y')} | {e['url'].split('/')[-1]}")

# Build RSS
rss = ET.Element('rss', {
    'version': '2.0',
    'xmlns:itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd',
    'xmlns:atom': 'http://www.w3.org/2005/Atom',
})
channel = ET.SubElement(rss, 'channel')

TITLE       = 'I Pizzini di Don Villa'
DESCRIPTION = 'I pensieri e gli insegnamenti di Don Villa'
WEBSITE     = 'https://pizzini-b5c63.web.app'
RSS_URL     = 'https://storage.googleapis.com/pizzini-91da9/podcast_feed.xml'
COVER_ART   = 'https://storage.googleapis.com/pizzini-91da9/podcast_cover.jpg'
AUTHOR      = 'Don Villa'
EMAIL       = 'skepee01@gmail.com'

ET.SubElement(channel, 'title').text = TITLE
ET.SubElement(channel, 'description').text = DESCRIPTION
ET.SubElement(channel, 'link').text = WEBSITE
ET.SubElement(channel, 'language').text = 'it'
ET.SubElement(channel, 'copyright').text = f'© {datetime.now().year} Don Villa'
ET.SubElement(channel, 'itunes:author').text = AUTHOR
ET.SubElement(channel, 'itunes:summary').text = DESCRIPTION
ET.SubElement(channel, 'itunes:explicit').text = 'no'
ET.SubElement(channel, 'itunes:category', {'text': 'Religion & Spirituality'})
ET.SubElement(channel, 'itunes:image', {'href': COVER_ART})
img = ET.SubElement(channel, 'image')
ET.SubElement(img, 'url').text = COVER_ART
ET.SubElement(img, 'title').text = TITLE
ET.SubElement(img, 'link').text = WEBSITE
owner = ET.SubElement(channel, 'itunes:owner')
ET.SubElement(owner, 'itunes:name').text = AUTHOR
ET.SubElement(owner, 'itunes:email').text = EMAIL
ET.SubElement(channel, '{http://www.w3.org/2005/Atom}link', {
    'href': RSS_URL, 'rel': 'self', 'type': 'application/rss+xml'
})

for e in eps:
    pub = e['dt'].strftime('%a, %d %b %Y %H:%M:%S GMT')
    item = ET.SubElement(channel, 'item')
    ET.SubElement(item, 'title').text = e['title']
    ET.SubElement(item, 'description').text = f"Episodio: {e['title']}"
    ET.SubElement(item, 'itunes:summary').text = f"Episodio: {e['title']}"
    ET.SubElement(item, 'pubDate').text = pub
    ET.SubElement(item, 'guid', {'isPermaLink': 'false'}).text = e['url']
    ET.SubElement(item, 'link').text = e['url']
    ET.SubElement(item, 'enclosure', {
        'url': e['url'],
        'type': 'audio/mpeg',
        'length': str(e['size']),
    })

# Save locally
rss_path = 'podcast_feed_clean.xml'
xml_bytes = ET.tostring(rss, encoding='utf-8')
dom = minidom.parseString(xml_bytes)
pretty = dom.toprettyxml(indent='  ', encoding='utf-8')
with open(rss_path, 'wb') as f:
    f.write(pretty)
print(f'\nSaved {rss_path}')

# Upload to Firebase
rss_blob = bucket.blob('podcast_feed.xml')
rss_blob.upload_from_filename(rss_path, content_type='application/rss+xml')
rss_blob.make_public()
print(f'Uploaded to Firebase: {rss_blob.public_url}')
print('Done.')
