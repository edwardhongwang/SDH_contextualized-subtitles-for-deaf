import yaml
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
from utils import load_config, to_server_constants
from .info import find_info


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


class ListingError(Exception):
    pass


@lru_cache
def find_listing(listing, clip_id):
    if not listing or clip_id is None:
        raise ListingError()
    constants = to_server_constants()
    listing_name = Path(listing).resolve().parts[-1]
    audio_path = find_audio_file(listing_name, clip_id)
    if not audio_path.is_file():
        raise ListingError()
    # Return audio path
    return audio_path


@lru_cache
def make_new_transcript(audio_path):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_speech_to_text_engine(
        L, config, audio_path, stt_engine="deepgram"
    ).split('```')[0]


@lru_cache
def add_edits(transcript):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_llm_proofreader(
        L, config, transcript
    ).split('```')[0]


@lru_cache
def add_sounds(transcript, audio_path):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return use_sound_describer(
        L, config, transcript, audio_path
    ).split('```')[0]


@lru_cache
def find_audio_file(listing, clip_id):
    constants = to_server_constants()
    listing_name = Path(listing).resolve().parts[-1]
    audio_root = Path(constants["api"]["audio_root"])
    input_folder = audio_root / listing_name / str(clip_id)
    ext = find_info(listing_name)[1].get("ext", "wav")
    return input_folder / f"voice.{ext}"


class TranscriptMaker:

    def __init__(self, add:set[str]):
        self.need = lambda key: key in add

    def __call__(self, listing: str, clip_id: int):
        audio_path = find_listing(listing, clip_id)
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

    def __call__(
        self, listing: str, clip_id: int, transcript: Transcript
    ):
        audio_path = find_listing(listing, clip_id)
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
