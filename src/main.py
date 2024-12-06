from .speech_transcriber import SpeechTranscriber
from .sound_description import non_speech_labeling
from .file_names import to_proofread_transcript_path
from .file_names import to_described_transcript_path
from .errors import APIError


def use_sound_describer(
    L, config, transcript, audio_path
):
    sound_config = config.get('sounds', {})
    return non_speech_labeling(
        L, transcript, audio_path, **{
            k:sound_config[k] for k in {
                "min_gap_duration", "context_lines"
            }
        }
    )


def use_speech_to_text_engine(
    L, config, audio_path, stt_engine
):
    transcriber = SpeechTranscriber(config)
    if stt_engine == "deepgram":
        try:
            return transcriber.transcribe_deepgram(
                audio_path
            )
        except UncategorizedError as e:
            L.error(e)
            assert False
    elif stt_engine == "groq":
        return transcriber.transcribe_groq(
            audio_path
        )
    assert False


def use_llm_proofreader(
    L, config, transcript
):
    transcriber = SpeechTranscriber(config)
    try:
        return transcriber.proofread_with_llm(transcript)
    except APIError as e:
        L.error(e)


def main(
    L, config, audio_path, transcript_path,
    stt_engine, describe_sounds
):
    # Run speech transcriber ( Groq or Deepgram )
    transcript = use_speech_to_text_engine(
        L, config, audio_path, stt_engine
    )
    # Write if output path provided
    if transcript_path is not None:
        with open(transcript_path, 'w') as wf:
            wf.write(transcript)

    # Run speech proofreader
    proofread_transcript = use_llm_proofreader(
        L, config, transcript
    )
    # Write if output path provided
    if transcript_path is not None:
        proofread_transcript_path = to_proofread_transcript_path(
            transcript_path
        )
        with open(proofread_transcript_path, "w") as wf:
            wf.write(proofread_transcript)
    
    # Skip sound descriptions
    if not describe_sounds:
        return proofread_transcript

    # Run sound describer
    described_transcript = use_sound_describer(
        L, config, proofread_transcript, audio_path
    )
    # Write if output path provided
    if transcript_path is not None:
        described_transcript_path = to_described_transcript_path(
            proofread_transcript_path
        )
        with open(described_transcript_path, "w") as wf:
            wf.write(described_transcript)

    return described_transcript
