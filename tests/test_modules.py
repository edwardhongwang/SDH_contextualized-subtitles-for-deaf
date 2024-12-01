"""
Test cases for all modules.
"""
import yaml
import logging
from pathlib import Path
from os.path import dirname


class TestException(Exception):
    pass


def test_speech_to_text(L, config):
    return [
        text for text in
        _test_speech_to_text(L, config)
    ]


def _test_speech_to_text(groq_api, config):
    ext = "mp3"
    model = "distil-whisper-large-v3-en"
    root_dir = Path(dirname(__file__)) / 'audio'
    audio_folders = [
        folder.resolve()
        for folder in root_dir.iterdir()
        if folder.is_dir()
    ]
    L = logging.getLogger(__name__)
    for folder in audio_folders:
        meta = folder / "meta.yaml"
        audio_path = folder / f"voice.{ext}"
        if not audio_path.exists():
            continue
        if meta.exists():
            info = yaml.safe_load(open(meta))
            label = info.get('label', meta)
            L.info(f'Processing {ext}: "{label}"')
            L.info(f'Using model: "{model}"')
            groq_data = groq_api(
                config.get('GROQ_API_KEY', ''),
                model, audio_path
            )
            text = groq_data.get("text", "")
            L.debug(text)
            yield text
