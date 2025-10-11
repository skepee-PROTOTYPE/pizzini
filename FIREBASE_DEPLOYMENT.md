# Firebase Deployment Guide for Pizzini Automation

## 🔥 **Firebase Setup Steps**

### **1. Prerequisites**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Install Python dependencies
pip install firebase-admin firebase-functions
```

### **2. Firebase Project Setup**

1. **Create Firebase Project**
   - Go to [Firebase Console](https://console.firebase.google.com/)
   - Click "Create a project"
   - Name it "pizzini-automation" (or your choice)
   - Enable Google Analytics (optional)

2. **Enable Required Services**
   - **Firestore Database**: For storing configuration and posting history
   - **Cloud Storage**: For storing your XML file
   - **Cloud Functions**: For the automation logic
   - **Cloud Scheduler**: For automatic posting (may require Blaze plan)

3. **Download Service Account Key**
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save as `serviceAccountKey.json` in your project folder

### **3. Project Configuration**

1. **Initialize Firebase in your project**
   ```bash
   firebase login
   firebase init
   ```
   
   Select:
   - ✅ Functions
   - ✅ Firestore
   - ✅ Storage
   - ✅ Hosting (optional)

2. **Update firebase.json** (already created)

3. **Update Firebase project ID** in `firebase_setup.py`:
   ```python
   'storageBucket': 'your-project-id.appspot.com'
   ```

### **4. Upload Configuration**

```bash
# Upload your config and XML to Firebase
python firebase_setup.py
```

This will:
- Upload your `config.json` to Firestore
- Upload your `pizzinifile.xml` to Cloud Storage
- Verify the setup

### **5. Deploy Functions**

```bash
# Deploy to Firebase
firebase deploy --only functions
```

### **6. Test Your Deployment**

```bash
# Get status
curl https://your-project-id.cloudfunctions.net/get_status

# Manual post
curl -X POST https://your-project-id.cloudfunctions.net/manual_post \
  -H "Content-Type: application/json" \
  -d '{"entry_id": 1}'

# Post random entry
curl -X POST https://your-project-id.cloudfunctions.net/manual_post
```

## 📊 **Firebase Functions Overview**

### **Scheduled Function**
- **Name**: `scheduled_post`
- **Schedule**: Daily at 6:00 AM (Italian time)
- **Purpose**: Automatically posts content
- **Trigger**: Cloud Scheduler

### **HTTP Functions**
- **`manual_post`**: Manually trigger a post
- **`get_status`**: Get automation status and recent posts

## 💰 **Pricing Estimate**

### **Free Tier Limits**
- **Cloud Functions**: 2M invocations/month (plenty!)
- **Firestore**: 1GB storage, 50K reads/day
- **Cloud Storage**: 5GB storage
- **Cloud Scheduler**: 3 jobs/month (may need Blaze plan)

### **Blaze Plan (Pay-as-you-go)**
- **Estimated monthly cost**: $0.10 - $2.00
- Only needed if you want reliable scheduling

## 🔧 **Configuration Management**

Your configuration is stored in Firestore at:
```
/config/social_media
```

To update configuration:
1. Modify local `config.json`
2. Run `python firebase_setup.py`
3. Redeploy functions if needed

## 📱 **Monitoring & Management**

### **Firebase Console Monitoring**
- Functions logs: Firebase Console > Functions > Logs
- Firestore data: Firebase Console > Firestore Database
- Storage files: Firebase Console > Storage

### **Cloud Logging**
- Detailed logs available in Google Cloud Console
- Set up alerts for errors

### **Manual Controls**
```bash
# Trigger immediate post
curl -X POST https://your-project-id.cloudfunctions.net/manual_post

# Check status
curl https://your-project-id.cloudfunctions.net/get_status
```

## 🔒 **Security Notes**

1. **Service Account Key**: Keep `serviceAccountKey.json` secure and private
2. **API Keys**: Stored securely in Firestore (not in code)
3. **Function Access**: Currently open (add authentication if needed)

## 🚀 **Advantages of Firebase Deployment**

✅ **Free/Low Cost**: Generous free tier
✅ **Reliable**: Google's infrastructure
✅ **Automatic Scaling**: Handles traffic spikes
✅ **Easy Monitoring**: Built-in logging and metrics
✅ **Global**: Fast worldwide performance
✅ **Maintenance-Free**: No server management

## 🔄 **Update Process**

To update your automation:
1. Modify code locally
2. Test locally: `firebase emulators:start`
3. Deploy: `firebase deploy --only functions`

## 📋 **Next Steps After Setup**

1. **Test the deployment** with manual posts
2. **Verify scheduling** (check logs after 6 AM Italian time)
3. **Monitor posting history** in Firestore
4. **Set up alerts** for function failures (optional)

Would you like me to help you set up any specific part of this Firebase deployment?