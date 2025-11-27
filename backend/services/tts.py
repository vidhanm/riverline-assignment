import os
import uuid
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def text_to_speech(text, voice_id=None):
    """
    Convert text to speech using Deepgram TTS REST API
    Returns audio file path or None if failed
    """
    try:
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            print("DEEPGRAM_API_KEY not set, skipping TTS")
            return None

        # Use provided voice_id or default
        voice = voice_id or "aura-asteria-en"

        # Generate unique filename
        audio_filename = f"{uuid.uuid4()}.mp3"
        audio_dir = Path("static/audio")
        audio_dir.mkdir(parents=True, exist_ok=True)
        audio_path = audio_dir / audio_filename

        # Call Deepgram REST API
        response = requests.post(
            "https://api.deepgram.com/v1/speak",
            headers={
                "Authorization": f"Token {api_key}",
                "Content-Type": "application/json"
            },
            params={"model": voice},
            json={"text": text}
        )

        # Check response
        if response.status_code != 200:
            print(f"TTS API error {response.status_code}: {response.text}")
            return None

        # Save binary audio to file
        with open(audio_path, "wb") as f:
            f.write(response.content)

        return str(audio_path)

    except Exception as e:
        print(f"TTS failed: {e}")
        return None  # Continue simulation without audio
