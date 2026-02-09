"""Upload podcast cover art to Firebase Storage"""
import firebase_admin
from firebase_admin import credentials, storage
import json
import os

def upload_cover_art(cover_path: str):
    """Upload podcast cover to Firebase Storage
    
    Args:
        cover_path: Path to cover image file
    """
    print(f"📤 Uploading podcast cover: {cover_path}")
    
    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate('serviceAccountKey.json')
        
        # Get project ID
        with open('serviceAccountKey.json', 'r') as f:
            cred_data = json.load(f)
            project_id = cred_data.get('project_id')
        
        firebase_admin.initialize_app(cred, {
            'storageBucket': project_id
        })
    
    bucket = storage.bucket()
    
    # Upload cover art
    blob = bucket.blob('podcast_cover.jpg')
    blob.upload_from_filename(cover_path)
    blob.make_public()
    
    public_url = blob.public_url
    print(f"✅ Cover uploaded!")
    print(f"🔗 Public URL: {public_url}")
    
    return public_url

if __name__ == '__main__':
    cover_file = 'PizziniDonVillaPodcastCover.jpg'
    
    if not os.path.exists(cover_file):
        print(f"❌ File not found: {cover_file}")
        print(f"Please make sure {cover_file} is in the current directory")
    else:
        url = upload_cover_art(cover_file)
        print(f"\n💡 Add this to config.json under podcast_info:")
        print(f'   "cover_art": "{url}"')
