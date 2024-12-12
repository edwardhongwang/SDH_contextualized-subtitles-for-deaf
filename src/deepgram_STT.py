from deepgram import (DeepgramClient, PrerecordedOptions, FileSource,)
from deepgram_captions import DeepgramConverter, srt
from .errors import APIError, TranscriptError


def speech_to_text(
    api_key, model, audio_path
):
    # STEP 1: Create a Deepgram client using the API key
    deepgram = DeepgramClient(api_key)
    # STEP 2: Configure Deepgram options for audio analysis
    options = PrerecordedOptions(
        model=model,
        detect_language=True,
        smart_format=True,
        utterances=True,
        utt_split=1.1,
    )
    try:
        with open(audio_path, "rb") as file:
            buffer_data = file.read()
    except FileNotFoundError as e:
        raise e
    payload: FileSource = {
        "buffer": buffer_data,
    }
    try:
        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)
    except Exception as e:
        raise APIError("Deepgrame API issue") from e
    try:
        # Take the "response" and pass into DeepgramConverter
        return srt(DeepgramConverter(response))
    except IndexError as e:
        raise TranscriptError("Transcription issue") from e
