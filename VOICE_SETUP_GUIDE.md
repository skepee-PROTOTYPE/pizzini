# 🎙️ Voice Options for Pizzini - Old Priest Edition

## ✅ Now Available: FREE Italian "Old Priest" Voices!

Your project now has **5 specially configured FREE voices** that sound like an Italian old priest, plus several other options!

---

## 🆓 FREE Voice Options (Recommended)

### **Old Priest Voices** (Coqui TTS - Best Quality, FREE)

1. **`priest-old-1`** ⭐ **RECOMMENDED** ⭐
   - Deep, contemplative Italian male voice
   - Slower, deliberate speech (85% speed)
   - Traditional, reverent tone
   - **Perfect for religious content**

2. **`priest-old-2`**
   - Wise, authoritative Italian elder
   - Slightly faster (88% speed)
   - Commanding presence

3. **`priest-warm`**
   - Compassionate, gentle priest voice
   - Warm and approachable (92% speed)
   - Comforting tone

4. **`coqui-it-male`**
   - Standard neutral Italian male
   - Normal speed
   - Clean, professional

5. **`coqui-it-female`**
   - Warm Italian female voice
   - Alternative option

### **Basic Voices** (gTTS - Simple, FREE)

- **`gtts-it-male-slow`** - Slower Italian male (robotic but clear)
- **`gtts-it-male`** - Normal speed Italian male
- **`gtts-it-male-it`** - Traditional Italy accent (slow)
- **`gtts-it-female`** - Italian female voice

---

## 💰 Paid Option (Azure TTS)

If you need Azure's premium voices, you still have access to:
- `azure-diego` - Mature male (best Azure option for priest)
- `azure-calimero` - Authoritative male
- `azure-benigno` - Warm male

**Note:** Azure requires API keys and costs money.

---

## 🚀 Quick Start

### Step 1: Install Coqui TTS (FREE)

```powershell
pip install TTS gTTS
```

### Step 2: Choose Your Voice

Edit [config.json](config.json) and change the voice:

```json
"audio_settings": {
  "voice": "priest-old-1",   // ⬅️ Change this!
  "add_intro": false,
  "output_directory": "audio_output"
}
```

**Voice options:**
- `priest-old-1` - Deep contemplative (RECOMMENDED)
- `priest-old-2` - Wise authoritative  
- `priest-warm` - Gentle compassionate
- `gtts-it-male-slow` - Simple slow voice

### Step 3: Test All Voices

Run the voice preview tool to hear all options:

```powershell
python preview_voices.py
```

This will generate audio samples for **every available voice** in the `voice_previews/` folder.

Listen to each one and pick your favorite!

---

## 🎧 Voice Preview Examples

### Test a Specific Voice:

```powershell
# Test the recommended old priest voice
python preview_voices.py priest-old-1

# Test the warm priest voice
python preview_voices.py priest-warm

# Test basic gTTS voice
python preview_voices.py gtts-it-male-slow
```

### Test ALL Voices at Once:

```powershell
python preview_voices.py
```

All audio files will be saved to `voice_previews/` for easy comparison.

---

## 📝 How to Use in Your Code

### Example 1: Generate Audio with Old Priest Voice

```python
from social_media_poster import AudioGenerator

# Initialize with old priest voice
generator = AudioGenerator(voice='priest-old-1')

# Generate audio
audio_file = generator.text_to_speech(
    text="Oggi riflettiamo sulla bellezza della fede...",
    title="Pizzino_20260210"
)

print(f"Audio saved: {audio_file}")
```

### Example 2: Create Podcast Episode

```python
episode = generator.create_podcast_episode(
    title="Riflessione del Giorno",
    content="Carissimi fratelli e sorelle...",
    date="2026-02-10"
)

print(f"Podcast ready: {episode['audio_path']}")
```

---

## 🆚 Comparison: Speechify vs Current Options

| Feature | Speechify | Coqui TTS (Your New Option) |
|---------|-----------|------------------------------|
| **Cost** | $139/year | **FREE** ✅ |
| **Quality** | High | **High** ✅ |
| **API Access** | ❌ No | **✅ Yes** |
| **Customization** | Limited | **Full control** ✅ |
| **Old Priest Voice** | ❌ No | **✅ Yes (3 options!)** |
| **Automation** | ❌ No | **✅ Yes** |

**Verdict:** Coqui TTS is **better for your project** and **100% FREE**!

---

## 🔧 Troubleshooting

### "Coqui TTS not available"

```powershell
pip install --upgrade TTS
```

### "gTTS not available"

```powershell
pip install --upgrade gTTS
```

### Audio is WAV instead of MP3

Install pydub for automatic MP3 conversion:

```powershell
pip install pydub
```

### Download is slow on first use

Coqui TTS downloads the voice model on first use (~100MB). This only happens once!

---

## 💡 Tips for Best Results

1. **Start with `priest-old-1`** - It's optimized for religious content
2. **Test multiple voices** - Run `python preview_voices.py` to compare
3. **Stay FREE** - No need for paid services! Coqui TTS quality is excellent
4. **Adjust speed** - You can modify the speed parameter in the code if needed

---

## 📊 Current Configuration

Your project is currently set to:
- **Voice:** `priest-old-1` (Deep contemplative old priest)
- **Service:** Coqui TTS (FREE)
- **Cost:** $0/month

---

## 📞 Need Help?

Run the preview tool to test voices:
```powershell
python preview_voices.py --help
```

Check available voices in code:
```python
from social_media_poster import AudioGenerator
AudioGenerator.list_available_voices()
```

---

**Enjoy your new FREE Italian old priest voices! 🎙️✝️**
