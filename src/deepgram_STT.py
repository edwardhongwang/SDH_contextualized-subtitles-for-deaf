from deepgram import (DeepgramClient, PrerecordedOptions, FileSource,)
import os
from deepgram_captions import DeepgramConverter, srt

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


def speech_to_text(audio_path):
    try:
        # STEP 1: Create a Deepgram client using the API key
        deepgram = DeepgramClient(DEEPGRAM_API_KEY)

        with open(audio_path, "rb") as file:
            buffer_data = file.read()

        payload: FileSource = {
            "buffer": buffer_data,
        }

        # STEP 2: Configure Deepgram options for audio analysis
        options = PrerecordedOptions(
            model="nova-2",  #### for model here can also use "whisper", "nova-2", "whisper-large"
            detect_language=True,
            smart_format=True,
            utterances=True,
            utt_split=1.1,
        )

        # STEP 3: Call the transcribe_file method with the text payload and options
        response = deepgram.listen.rest.v("1").transcribe_file(payload, options)

        # Take the "response" result from transcribe_file() and pass into DeepgramConverter
        transcription = srt(DeepgramConverter(response))

        # Get directory and base name of the audio file
        audio_dir = os.path.dirname(audio_path)
        audio_filename = os.path.basename(audio_path)
        base_name, _ = os.path.splitext(audio_filename)

        # Create the transcript filename with .srt extension
        transcript_filename = f"transcript_{options.model}_{base_name}.srt"
        transcript_path = os.path.join(audio_dir, transcript_filename)

        # Save the transcription to the .srt file
        with open(transcript_path, 'w', encoding='utf-8') as f:
            f.write(transcription)

        print(f"Transcription saved to {transcript_path}")
        
        # Return the transcript file path
        return transcript_path

    except Exception as e:
        print(f"Exception: {e}")
        return None


if __name__ == "__main__":
    audio_path = "example_audio_path.wav"
    transcript_path = speech_to_text(audio_path)
    if transcript_path:
        print(f"Transcript saved at {transcript_path}")
    else:
        print("Transcription failed.")
