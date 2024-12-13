from functools import lru_cache 
from pathlib import Path
import yaml


@lru_cache
def to_server_constants():
    return yaml.safe_load(open(
        "./server/constants.yaml"
    ))


@lru_cache
def find_figure_label_folder():
    constants = to_server_constants()
    return Path(constants["api"]["figure_root"])


@lru_cache
def trim_listing_name(listing):
    return Path(listing).resolve().parts[-1]

@lru_cache
def find_listing_info(listing):
    audio_root = find_audio_root_folder()
    listing_name = trim_listing_name(listing) 
    folder = audio_root / listing_name
    return (
        yaml.safe_load(open(folder / "info.yaml"))
    )


@lru_cache
def find_audio_root_folder():
    constants = to_server_constants()
    return Path(constants["api"]["audio_root"])


@lru_cache
def find_audio_file(listing, clip_id):
    audio_root = find_audio_root_folder()
    listing_name = Path(listing).resolve().parts[-1]
    input_folder = audio_root / listing_name / str(clip_id)
    ext = find_listing_info(listing_name).get(
        "ext", "wav"
    )
    return input_folder / f"voice.{ext}"


@lru_cache
def find_audio_listings():
    audio_root = find_audio_root_folder()
    if not Path(audio_root).is_dir():
        return []
    return [
        str(x) for x in Path(audio_root).iterdir()
        if x.is_dir()
    ]
