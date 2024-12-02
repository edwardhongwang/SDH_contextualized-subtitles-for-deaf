from deepgram import (DeepgramClient, PrerecordedOptions, FileSource,)
from deepgram_captions import DeepgramConverter, srt
from .errors import UncategorizedError 


def speech_to_text(
    api_key, model, audio_path
):
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(api_key)

        with open(audio_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model=model,
            detect_language=True,
            smart_format=True,
            utterances=True,
            utt_split=1.1,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        # Take the "response" result from transcribe_file() and pass into DeepgramConverter
        transcription = srt(DeepgramConverter(response))

        # Return the transcript text
        return transcription

    except Exception as e:
        raise UncategorizedError(
            "Transcription issue"
        ) from e
