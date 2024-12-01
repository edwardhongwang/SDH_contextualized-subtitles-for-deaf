"""
Speech to text module handling transcription and speaker diarization.
"""
from . import groq_audio_api


class SpeechTranscriber:
    def __init__(self, config):
        # Initialize STT services (Google, Whisper)
        self.groq_key = config.get('GROQ_API_KEY', '')
        self.model = "distil-whisper-large-v3-en"
        # Initialize diarization
        # TODO

    def transcribe(self, audio_path):
        groq_data = groq_audio_api(
            self.groq_key, self.model, audio_path
        )
        return groq_data.get("text", "")

    def validate_confidence(self, transcript):
        # Handle confidence scores
        # Cross-validate low confidence segments
        # TODO
        pass
