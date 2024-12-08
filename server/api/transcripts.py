import logging
from pathlib import Path
from datetime import timedelta
from functools import lru_cache 
from pydantic import BaseModel
from pydantic import RootModel
from typing import List

from src import use_speech_to_text_engine
from src import use_llm_proofreader
from src import use_sound_describer
from utils import parse_srt, format_srt
from utils import load_config


class TranscriptLine(BaseModel):
    start_time: timedelta 
    end_time: timedelta 
    index: int
    text: str


class Transcript(RootModel):
    root: List[TranscriptLine]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class TranscriptError(Exception):
    pass


@lru_cache
def find_listing(listing):
    if not listing:
        raise TranscriptError()
    folder = Path(listing).resolve().parts[-1]
    static = Path("server/client/static")
    input_folder = static / folder
    audio_path = input_folder / "voice.mp3"
    if not input_folder.is_dir():
        raise TranscriptError()
    if not audio_path.is_file():
        raise TranscriptError()
    # Return input folder and audio path
    return input_folder, audio_path


@lru_cache
def make_new_transcript(audio_path):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_speech_to_text_engine(
        L, config, audio_path, stt_engine="deepgram"
    )


@lru_cache
def add_edits(transcript):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_llm_proofreader(
        L, config, transcript
    )


@lru_cache
def add_sounds(transcript, audio_path):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_sound_describer(
        L, config, transcript, audio_path
    )


class TranscriptMaker:

    def __init__(self, add:set[str]):
        self.need = lambda key: key in add

    def __call__(self, listing: str):
        input_folder, audio_path = find_listing(
            listing
        )
        # Handle creation from scratch
        transcript = make_new_transcript(audio_path)
        if self.need("edits"):
            transcript = add_edits(transcript)
        if self.need("sounds"):
            transcript = add_sounds(transcript, audio_path)
        # Return transcript
        return parse_srt(
            transcript
        )


class TranscriptEnricher:

    def __init__(self, add:set[str], has:set[str]):
        self.need = lambda key: key in (add-has)

    def __call__(self, listing: str, transcript: Transcript):
        input_folder, audio_path = find_listing(
            listing
        )
        # Serialize transcript
        transcript = format_srt(transcript.model_dump())
        # Handle updates to existing transcript
        if self.need("edits"):
            transcript = add_edits(transcript)
        if self.need("sounds"):
            transcript = add_sounds(transcript, audio_path)
        # Return transcript
        return parse_srt(
            transcript
        )


# Possible transcript initializations
initializations = [
    (), ("edits",), ("edits", "sounds", "emotions")
]
# Possible transcript transformations
transformations = {
    ("edits",): [
        ()
    ],
    ("sounds",): [
        (), ("edits",)
    ],
    ("emotions",): [
        (), ("edits",), ("sounds",),
        ("edits","sounds")
    ],
    ("sounds","emotions"): [
        (), ("edits",)
    ],
    ("edits","sounds","emotions"): [
        (),
    ]
}
# Handle transcript initializations
makers = {
    tuple(target): TranscriptMaker(add=set(target))
    for target in initializations
}
# Handle transcript transformations
enrichers = {
    target: {
        source: TranscriptEnricher(
            add=set(target), has=set(source)
        )
        for source in sources
    }
    for target, sources in transformations.items()
}
