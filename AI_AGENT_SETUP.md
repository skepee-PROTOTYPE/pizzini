# AI Agent Setup Guide

## Overview
Your AI agent uses Google Gemini 1.5 Flash (FREE) to make intelligent decisions about:
- **When** to post (optimal timing based on engagement)
- **What** to post (content selection based on relevance)
- **Validation** (auto-check and fix issues)

## Step 1: Get Free Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Get API Key"** or **"Create API Key"**
4. Copy the API key (starts with `AIza...`)

## Step 2: Add API Key to Firebase Config

### Option A: Via sync script (Recommended)
1. Open `functions/config.json`
2. Find the `ai_agent` section
3. Replace `YOUR_GEMINI_API_KEY_HERE` with your actual API key
4. Run: `python sync_config_to_firebase.py`

### Option B: Manually update Firestore
1. Go to [Firebase Console](https://console.firebase.google.com/project/pizzini-91da9/firestore)
2. Navigate to `config` → `social_media` document
3. Add field: `ai_agent.gemini_api_key` = `YOUR_API_KEY`

## Step 3: Create AI Scheduler Job

Run this command to create hourly AI checks:

```bash
gcloud scheduler jobs create http ai-scheduled-post ^
  --schedule="0 * * * *" ^
  --uri="https://us-central1-pizzini-91da9.cloudfunctions.net/ai_scheduled_post" ^
  --http-method=POST ^
  --time-zone="Europe/Rome" ^
  --location=us-central1 ^
  --description="AI-powered hourly check for intelligent posting"
```

**What this does:**
- Runs every hour (0 * * * *)
- AI decides: "Should I post now?"
- If yes → selects best episode and posts
- If no → waits for next hour

## Step 4: Test the AI Agent

### Test AI Decision (without posting):
```bash
curl -X POST https://us-central1-pizzini-91da9.cloudfunctions.net/ai_scheduled_post
```

Check logs:
```bash
gcloud functions logs read ai_scheduled_post --region=us-central1
```

## How It Works

### Hourly Check Flow:
```
Every hour:
├─ AI checks: "Should I post now?"
│  ├─ Analyzes: hours since last post
│  ├─ Considers: current time of day
│  └─ Evaluates: engagement patterns
│
├─ If YES:
│  ├─ AI selects: best episode for today
│  ├─ Generates: podcast audio
│  ├─ Posts: Facebook + podcast
│  └─ Validates: everything worked
│
└─ If NO:
   └─ Logs: "Waiting, only 6 hours since last post"
```

### AI Decision Factors:
- ✅ Time since last post (23-26 hour window)
- ✅ Current hour (prefers 7-9 AM)
- ✅ Day of week patterns
- ✅ Historical engagement data
- ✅ Upcoming holidays (Valentine's Day, Easter, etc.)
- ✅ Content variety (avoids repeating themes)

## Monitoring AI Decisions

All AI decisions are logged to Firestore:
- Collection: `ai_decisions`
- See why AI decided to post/wait
- Track confidence levels
- Review episode selections

View recent decisions:
```bash
# In Firebase Console → Firestore → ai_decisions
```

## Cost Breakdown

| Component | Usage | Cost |
|-----------|-------|------|
| Google Gemini API | ~24 requests/day | **$0** (FREE tier: 1,500/day) |
| Cloud Scheduler | 24 runs/day | **$0** (FREE tier: 3 jobs) |
| Cloud Functions | 24 invocations/day | **$0** (FREE tier: 2M/month) |
| Firebase Storage | Same as before | **$0** |
| **TOTAL** | | **$0/month** |

## Switching Between AI and Fixed Schedule

### Use AI Agent (Intelligent):
- Scheduler runs hourly
- AI decides when to post
- Optimal timing and content selection

### Use Fixed Schedule (Current):
- Scheduler runs at 6 AM daily
- Always posts at same time
- Predictable and simple

Both can run simultaneously! AI will respect "hours since last post" rule.

## Troubleshooting

### "Gemini API key not found"
→ Check config: `ai_agent.gemini_api_key` exists in Firestore

### "AI decided not to post" every hour
→ Check Firestore `posting_activity` - may think recent post exists
→ Verify scheduler timezone is Europe/Rome

### AI always picks same episode
→ Check if episodes are marked as posted in `posting_activity`
→ Ensure different themes in episode descriptions

### Want to force a post now?
```bash
curl -X POST https://us-central1-pizzini-91da9.cloudfunctions.net/scheduled_post
```
(Uses old non-AI function, posts next sequential episode immediately)

## Next Steps

1. ✅ Get Gemini API key
2. ✅ Add to config and sync
3. ✅ Deploy updated functions
4. ✅ Create AI scheduler job
5. ✅ Monitor first 24 hours
6. 📊 Review AI decisions in Firestore
7. 🎯 Adjust rules if needed (edit `ai_agent.posting_rules` in config)

---

**Questions? Check logs:**
```bash
gcloud functions logs read ai_scheduled_post --region=us-central1 --limit=50
```
