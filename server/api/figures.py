import io
import soundfile as sf
from pathlib import Path
from datetime import timedelta
from functools import lru_cache 
from collections import OrderedDict 
from tvsm_extractor import load_labels, vectorize_transcript 
from tvsm_extractor import Parameters, Plotter
from .transcripts import find_listing 
from .transcripts import TranscriptMaker
from data_utils import find_figure_label_folder
from data_utils import find_listing_info
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('AGG')


from matplotlib.colors import ListedColormap
from librosa.display import waveshow
import numpy as np


class FigureError(Exception):
    pass


def make_image(fig):
    img_buf = io.BytesIO()
    plt.savefig(
        img_buf, format='png', transparent=True
    )
    img_buf.seek(0)
    return img_buf


@lru_cache
def load_audio(audio_path):
    return sf.read(audio_path)


def generate_figure(
    label_root, transcript, audio_path,
    figure_id, clip_id, duration 
):
    audio, samplerate = load_audio(audio_path)
    start_time = timedelta(seconds=(
        duration * clip_id if duration else 0
    ))
    end_time = start_time + timedelta(
        seconds = audio.shape[0] / samplerate
    )
    label_dict = OrderedDict()
    label_dict["Automated speech timings"] = vectorize_transcript(
        transcript, timedelta(seconds=0), end_time - start_time
    )
    if figure_id:
        label_dict["Real speech timings"] = load_labels(
            label_root, figure_id, start_time, end_time
        )
    Parameters.sample_rate = samplerate
    parameters = Parameters(15, 'serif')
    with Plotter(audio, label_dict, parameters) as fig: 
        return make_image(fig)


class FigureMaker:

    def __init__(self, add:set[str]):
        self.maker = TranscriptMaker(add=add)

    def __call__(self, listing: str, clip_id: int):
        info = find_listing_info(listing)
        audio_path = find_listing(listing, clip_id)
        if not audio_path.is_file():
            raise TranscriptError()
        transcript = self.maker(listing, clip_id)
        duration = info.get("clip_duration", None)
        clip_count = info.get("clip_count", 1)
        figure_id = info.get("figure", None)
        if clip_id >= clip_count:
            raise FigureError()
        # Sound labels and waveform
        return generate_figure(
            find_figure_label_folder(), transcript, audio_path,
            figure_id, clip_id, duration 
        )

# Possible figure initializations
initializations = [
    (), ("edits",), ("sounds",),
    ("edits", "sounds", "emotions") 
]
# Handle figure initializations
figure_makers = {
    tuple(target): FigureMaker(add=set(target))
    for target in initializations
}
