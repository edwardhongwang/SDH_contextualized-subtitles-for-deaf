import os


def audio_path_to_transcript_path(audio_path, model="unknown"):
    # Get directory and base name of the audio file
    audio_dir = os.path.dirname(audio_path)
    audio_filename = os.path.basename(audio_path)
    base_name, _ = os.path.splitext(audio_filename)

    # Create the transcript filename with .srt extension
    transcript_filename = f"transcript_{model}_{base_name}.srt"
    return os.path.join(audio_dir, transcript_filename)


def to_proofread_transcript_path(transcript_path):
    # Determine the output path
    transcript_dir = os.path.dirname(transcript_path)
    transcript_filename = os.path.basename(transcript_path)
    proofread_filename = f"proofread_{transcript_filename}"
    return os.path.join(transcript_dir, proofread_filename)


def create_output_transcript_path(
    output_path, audio_path, stt_engine
):
    return output_path if output_path else (
        audio_path_to_transcript_path(
            audio_path, stt_engine
        )
    )



