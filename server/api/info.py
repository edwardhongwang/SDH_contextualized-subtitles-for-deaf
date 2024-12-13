import yaml
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from pydantic import RootModel
from fastapi import Depends
from typing import List

from data_utils import (
    find_listing_info, find_audio_listings,
    trim_listing_name
)
from utils import load_config


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


def to_info_line(listing):
    try:
        listing_name = trim_listing_name(listing)
        info = find_listing_info(listing)
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
        self, listings=Depends(find_audio_listings)
    ):
        info_index = []
        for listing in listings:
            info_index.append(to_info_line(listing)) 
        return InfoIndex(info_index)


def list_figures():
    figure_list = []
    listings = find_audio_listings()
    try:
        info_index = InfoIndexer()(listings)
    except InfoError:
        return figure_list
    for idx in info_index:
        if idx.figure is None:
            continue
        figure_list.append(idx.listing)
    return figure_list 