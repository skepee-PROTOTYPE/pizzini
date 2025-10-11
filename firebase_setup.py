#!/usr/bin/env python3
"""
Firebase Setup Script for Pizzini Automation
Uploads configuration and XML content to Firebase
"""

import json
import sys
import os
from firebase_admin import initialize_app, firestore, storage, credentials
import argparse

def setup_firebase_config(config_file='config.json'):
    """Upload configuration to Firestore"""
    try:
        # Initialize Firebase Admin SDK
        # You'll need to download your service account key from Firebase Console
        if not os.path.exists('serviceAccountKey.json'):
            print("❌ Missing serviceAccountKey.json")
            print("📋 Download it from Firebase Console > Project Settings > Service Accounts")
            return False
        
        cred = credentials.Certificate('serviceAccountKey.json')
        initialize_app(cred, {
            'storageBucket': 'pizzini-91da9.appspot.com'  # Your actual project ID
        })
        
        # Load local config
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Upload to Firestore
        db = firestore.client()
        config_ref = db.collection('config').document('social_media')
        config_ref.set(config)
        
        print("✅ Configuration uploaded to Firestore")
        return True
        
    except Exception as e:
        print(f"❌ Failed to setup Firebase config: {e}")
        return False

def upload_xml_content(xml_file='pizzinifile.xml'):
    """Upload XML content to Firebase Storage"""
    try:
        # Upload XML file to Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        
        with open(xml_file, 'r', encoding='utf-8') as f:
            blob.upload_from_string(f.read(), content_type='application/xml')
        
        print("✅ XML content uploaded to Firebase Storage")
        return True
        
    except Exception as e:
        print(f"❌ Failed to upload XML content: {e}")
        return False

def test_functions():
    """Test Firebase Functions locally"""
    print("🧪 Testing Firebase Functions...")
    print("Run this command to test locally:")
    print("firebase emulators:start --only functions")
    print("\nThen test endpoints:")
    print("- GET  http://localhost:5001/your-project/us-central1/get_status")
    print("- POST http://localhost:5001/your-project/us-central1/manual_post")

def main():
    parser = argparse.ArgumentParser(description='Setup Pizzini automation on Firebase')
    parser.add_argument('--config', default='config.json', help='Configuration file')
    parser.add_argument('--xml', default='pizzinifile.xml', help='XML content file')
    parser.add_argument('--test', action='store_true', help='Show test instructions')
    
    args = parser.parse_args()
    
    print("🔥 Firebase Pizzini Automation Setup")
    print("=" * 40)
    
    if args.test:
        test_functions()
        return
    
    success = True
    
    # Setup configuration
    if os.path.exists(args.config):
        success &= setup_firebase_config(args.config)
    else:
        print(f"❌ Configuration file {args.config} not found")
        success = False
    
    # Upload XML content
    if os.path.exists(args.xml):
        success &= upload_xml_content(args.xml)
    else:
        print(f"❌ XML file {args.xml} not found")
        success = False
    
    if success:
        print("\n🎉 Firebase setup complete!")
        print("📋 Next steps:")
        print("1. Deploy functions: firebase deploy --only functions")
        print("2. Test status: curl https://your-project.cloudfunctions.net/get_status")
        print("3. Manual post: curl -X POST https://your-project.cloudfunctions.net/manual_post")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()