from .speech_transcriber import SpeechTranscriber
from .sound_description import non_speech_labeling
from .file_names import to_proofread_transcript_path
from .file_names import to_described_transcript_path
from .errors import APIError


def use_sound_describer(
    L, config, transcript_path, audio_path
):
    sound_config = config.get('sounds', {})
    return non_speech_labeling(
        L, transcript_path, audio_path, **{
            k:sound_config[k] for k in {
                "min_gap_duration", "context_lines"
            }
        }
    )


def use_speech_to_text_engine(
    L, config, audio_path, stt_engine, describe_sounds
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
    L, config, transcript_path
):
    transcriber = SpeechTranscriber(config)
    try:
        return transcriber.proofread_with_llm(
            open(transcript_path).read()
        )
    except APIError as e:
        L.error(e)


def main(
    L, config, audio_path, transcript_path,
    stt_engine, describe_sounds
):
    # Run speech transcriber ( Groq or Deepgram )
    transcribed = use_speech_to_text_engine(
        L, config, audio_path, stt_engine, describe_sounds
    )
    with open(transcript_path, 'w') as wf:
        wf.write(transcribed)

    # Run speech proofreader
    proofread_transcript = use_llm_proofreader(
        L, config, transcript_path
    )
    proofread_transcript_path = to_proofread_transcript_path(
        transcript_path
    )
    with open(proofread_transcript_path, "w") as wf:
        wf.write(proofread_transcript)

    if not describe_sounds:
        return proofread_transcript

    # Run sound describer
    described_transcript = use_sound_describer(
        L, config, proofread_transcript_path, audio_path
    )
    described_transcript_path = to_described_transcript_path(
        proofread_transcript_path
    )
    with open(described_transcript_path, "w") as wf:
        wf.write(described_transcript)

    return described_transcript
