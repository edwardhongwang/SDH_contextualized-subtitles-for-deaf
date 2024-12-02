"""
Speech to text module handling transcription and speaker diarization.
"""
import os
from dotenv import load_dotenv
from .llm import proofread
from .deepgram_STT import speech_to_text
from .groq_STT import groq_audio_api


load_dotenv()


class SpeechTranscriber:
    def __init__(self, config):
        # Initialize LLM services ( OpenAI )
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.openai_model = config.get('openai', {}).get(
            'model', "o1-preview-2024-09-12"
        )
        # Initialize STT services ( Deepgram, Google, Groq )
        self.deepgram_key = os.getenv('DEEPGRAM_API_KEY')
        self.google_key = os.getenv('GOOGLE_API_KEY')
        self.groq_key = os.getenv('GROQ_API_KEY')
        self.groq_model = config.get('groq', {}).get(
            'model', "distil-whisper-large-v3-en"
        )
        self.groq_temperature = config.get('groq', {}).get(
            'temperature', 0 
        )
        self.deepgram_model = config.get('deepgram', {}).get(
            'model', 'nova-2'
        )

    def proofread_with_llm(self, transcript_path): 
        model = self.openai_model
        return proofread(
            self.openai_key, model, transcript_path
        )

    def transcribe_deepgram(self, audio_path):
        model = self.deepgram_model
        return speech_to_text(
            self.deepgram_key, model, audio_path
        )

    def transcribe_groq(self, audio_path):
        temperature = self.groq_temperature
        model = self.groq_model
        groq_data = groq_audio_api(
            self.groq_key, model, audio_path,
            temperature=temperature
        )
        return groq_data.get("text", "").strip()

    def validate_confidence(self, transcript):
        # Handle confidence scores
        # Cross-validate low confidence segments
        # TODO
        pass
