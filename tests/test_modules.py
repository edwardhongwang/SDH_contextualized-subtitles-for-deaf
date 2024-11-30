"""
Test cases for all modules.
""" 
import yaml
import requests
from pathlib import Path
from os.path import dirname


class TestException(Exception):
    pass


def test_speech_to_text(L, config):
    return [
        text for text in
        _test_speech_to_text(L, config)
    ]


def _test_speech_to_text(L, config):
    ext = "mp3"
    model = "distil-whisper-large-v3-en"
    root_dir = Path(dirname(__file__)) / 'audio'
    audio_folders = [
        folder.resolve()
        for folder in root_dir.iterdir()
        if folder.is_dir()
    ]
    for folder in audio_folders:
        meta = folder / "meta.yaml"
        voice = folder / f"voice.{ext}"
        if not voice.exists():
            continue
        if meta.exists():
            info = yaml.safe_load(open(meta))
            label = info.get('label',meta)
            L.info(f'Processing {ext}: "{label}"')
            L.info(f'Using model: "{model}"')
            groq_data = groq_api(
                L, config, model, voice, ext
            )
            text = groq_data.get("text", "")
            L.debug(text)
            yield text 


def groq_api(
        L, config, model, voice, ext,
        lang="en", temp=0
    ):
    groq_key = config.get(
        'GROQ_API_KEY', ''
    )
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
        f'0.{ext}', open(voice, 'rb').read()
    )
    files = {
        'file': file,
        'model': (None, model),
        'language': (None, lang),
        'temperature': (None, temp),
        'response_format': (None, 'json'),
    }
    try:
        response = requests.post(
            endpoint, headers=headers, files=files
        )
    except requests.exceptions.ConnectionError:
        raise TestException(
            "Unable to contact API server"
        ) from None
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        raise TestException(
            "Invalid JSON Response from server"
        ) from None
