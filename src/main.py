from .speech_transcriber import SpeechTranscriber
from .file_names import to_proofread_transcript_path
from .errors import APIError

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
    stt_engine
):
    # Run speech transcriber ( Groq or Deepgram )
    transcribed = use_speech_to_text_engine(
        L, config, audio_path, stt_engine
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

    return proofread_transcript
