"""Create a cloud function to upload the real XML file"""
from firebase_functions import https_fn
from firebase_admin import storage
import json

@https_fn.on_request()
def upload_real_xml(req):
    """Upload the real pizzinifile.xml from request body"""
    try:
        # Get XML content from request
        xml_content = req.get_data(as_text=True)
        
        if not xml_content:
            return {"status": "error", "message": "No XML content provided"}
        
        # Upload to Firebase Storage
        bucket = storage.bucket()
        blob = bucket.blob('pizzinifile.xml')
        blob.upload_from_string(xml_content, content_type='application/xml')
        
        return {
            "status": "success",
            "message": f"Uploaded {len(xml_content)} bytes to pizzinifile.xml",
            "size": len(xml_content)
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
