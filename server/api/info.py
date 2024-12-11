import yaml
from pathlib import Path
from typing import Optional
from functools import lru_cache 
from pydantic import BaseModel
from pydantic import RootModel
from fastapi import Depends
from typing import List

from utils import load_config, to_server_constants


class InfoLine(BaseModel):
    label: str
    source: str
    speaker: str
    listing: str
    clip_count: int 
    figure: Optional[int]


class InfoIndex(RootModel):
    root: List[InfoLine]

    def __iter__(self):
        return iter(self.root)

    def __getitem__(self, item):
        return self.root[item]


class InfoError(Exception):
    pass


@lru_cache
def find_info(listing):
    constants = to_server_constants()
    listing_name = Path(listing).resolve().parts[-1]
    audio_root = Path(constants["api"]["audio_root"])
    folder = audio_root / listing_name
    return (
        listing_name,
        yaml.safe_load(open(folder / "info.yaml"))
    )


def to_info_line(listing):
    try:
        listing_name, info = find_info(listing)
    except FileNotFoundError:
        raise InfoError()
    return InfoLine(**{
        "listing": listing_name,
        "label": info["label"],
        "source": info["source"],
        "speaker": info["speaker"],
        "figure": info.get("figure", None),
        "clip_count": info.get("clip_count", 1)
    })


class InfoFinder:

    def __init__(self):
        pass

    def __call__(self, listing: str):
        try:
            return to_info_line(listing)
        except FileNotFoundError:
            raise InfoError()


class InfoIndexer:

    def __init__(self):
        pass

    def __call__(
        self, constants=Depends(to_server_constants)
    ):
        audio_root = Path(
            constants["api"]["audio_root"]
        )
        if not audio_root.is_dir():
            raise InfoError()

        listings = [
            str(x) for x in Path(audio_root).iterdir()
            if x.is_dir()
        ]
        info_index = []
        for listing in listings:
            info_index.append(to_info_line(listing)) 
        return InfoIndex(info_index)
