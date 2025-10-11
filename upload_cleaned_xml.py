"""Upload cleaned XML file to Firebase Storage"""
from google.cloud import storage
import firebase_admin
from firebase_admin import credentials, storage as admin_storage

# Initialize Firebase (if not already initialized)
try:
    firebase_admin.get_app()
except ValueError:
    firebase_admin.initialize_app()

# Get the storage bucket
bucket = admin_storage.bucket('pizzini-91da9.appspot.com')

# Upload the file
blob = bucket.blob('pizzinifile.xml')
blob.upload_from_filename('pizzinifile.xml', content_type='application/xml')

print("✓ Successfully uploaded cleaned pizzinifile.xml to Firebase Storage")
print(f"  File size: {blob.size} bytes")
print(f"  Updated: {blob.updated}")
