"""
Voice Preview Tool - Test all available Italian voices for Pizzini
Generates sample audio with each voice so you can choose your favorite old priest voice
"""
import os
import sys
from social_media_poster import AudioGenerator

# Sample text - a typical pizzini message
SAMPLE_TEXT = """
Carissimi fratelli e sorelle, oggi riflettiamo sulla bellezza della fede 
e sull'importanza della preghiera quotidiana. Che il Signore vi benedica e 
vi guidi sempre sulla via della pace e della serenità.
"""

def preview_all_voices():
    """Generate audio samples for all available voices"""
    
    print("\n" + "="*70)
    print("🎙️  PIZZINI VOICE PREVIEW TOOL")
    print("="*70)
    
    # Get all available voices
    voices = AudioGenerator.list_available_voices()
    
    if not voices:
        print("\n❌ No TTS services available!")
        print("Install at least one: pip install TTS gTTS")
        return
    
    print(f"\n📋 Found {len(voices)} voices available\n")
    
    # Create preview directory
    preview_dir = "voice_previews"
    os.makedirs(preview_dir, exist_ok=True)
    
    # Group voices by service
    services = {}
    for voice in voices:
        service = voice['service']
        if service not in services:
            services[service] = []
        services[service].append(voice)
    
    # Generate previews for each voice
    for service, voice_list in services.items():
        print(f"\n{'─'*70}")
        print(f"  {service}")
        print(f"{'─'*70}\n")
        
        for i, voice in enumerate(voice_list, 1):
            voice_key = voice['key']
            description = voice.get('description', voice_key)
            
            print(f"{i}. {description}")
            print(f"   Key: {voice_key}")
            
            try:
                # Generate audio
                generator = AudioGenerator(voice=voice_key, output_dir=preview_dir)
                audio_path = generator.text_to_speech(
                    SAMPLE_TEXT, 
                    title=f"preview_{voice_key}"
                )
                
                # Get file size
                size_kb = os.path.getsize(audio_path) / 1024
                print(f"   ✅ Generated: {os.path.basename(audio_path)} ({size_kb:.1f} KB)")
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
            
            print()
    
    print("="*70)
    print(f"✅ Voice previews saved to: {os.path.abspath(preview_dir)}/")
    print("="*70)
    print("\n🎧 Listen to each voice and choose your favorite!")
    print("\nTo use a voice, update config.json:")
    print('   "voice": "priest-old-1"  // Replace with your chosen voice key')
    print("\n")


def preview_single_voice(voice_key: str):
    """Generate preview for a single voice"""
    
    print(f"\n🎙️  Generating preview for: {voice_key}")
    
    preview_dir = "voice_previews"
    os.makedirs(preview_dir, exist_ok=True)
    
    try:
        generator = AudioGenerator(voice=voice_key, output_dir=preview_dir)
        audio_path = generator.text_to_speech(
            SAMPLE_TEXT, 
            title=f"preview_{voice_key}"
        )
        
        print(f"✅ Audio generated: {audio_path}")
        print(f"🎧 Listen to evaluate the voice!")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def show_help():
    """Show usage instructions"""
    print("\n" + "="*70)
    print("🎙️  PIZZINI VOICE PREVIEW TOOL - USAGE")
    print("="*70)
    print("\nUsage:")
    print("  python preview_voices.py              # Preview all available voices")
    print("  python preview_voices.py priest-old-1 # Preview specific voice")
    print("  python preview_voices.py --help       # Show this help")
    print("\nAvailable voice keys:")
    
    voices = AudioGenerator.list_available_voices()
    for voice in voices:
        print(f"  • {voice['key']:20} - {voice.get('description', '')}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h', 'help']:
            show_help()
        else:
            preview_single_voice(sys.argv[1])
    else:
        preview_all_voices()
