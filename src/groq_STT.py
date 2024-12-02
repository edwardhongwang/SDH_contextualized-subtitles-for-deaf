"""
Calls to Groq Audio Transcription endpoint
"""
import requests
from pathlib import Path


def groq_audio_api(
    groq_key, model, audio_path,
    lang="en", temperature=0
):
    ext = Path(audio_path).suffix
    groq_url = (
        'https://api.groq.com/openai/v1'
    )
    endpoint = (
        f'{groq_url}/audio/transcriptions'
    )
    headers = {
        'Authorization': 'bearer ' + groq_key
    }
    # Protects the identity of the local filepath
    file = (
        f'0.{ext}', open(audio_path, 'rb').read()
    )
    files = {
        'file': file,
        'model': (None, model),
        'language': (None, lang),
        'temperature': (None, temperature),
        'response_format': (None, 'json'),
    }
    try:
        response = requests.post(
            endpoint, headers=headers, files=files
        )
    except requests.exceptions.ConnectionError:
        raise Exception(
            "Unable to contact API server"
        ) from None
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        raise Exception(
            "Invalid JSON Response from server"
        ) from None
