"""
Upload XML file to Firebase Storage
"""

import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase Admin
firebase_admin.initialize_app()

# Get storage bucket
bucket = storage.bucket()

# Upload the XML file
blob = bucket.blob('pizzinifile.xml')
with open('pizzinifile.xml', 'rb') as f:
    blob.upload_from_file(f)

print("✅ Successfully uploaded pizzinifile.xml to Firebase Storage")
print(f"📁 File available at: gs://{bucket.name}/pizzinifile.xml")