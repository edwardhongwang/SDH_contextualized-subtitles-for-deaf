import io
import soundfile as sf
from pathlib import Path
from datetime import timedelta
from functools import lru_cache 
from collections import OrderedDict 
from tvsm_extractor import load_labels, vectorize_transcript 
from tvsm_extractor import Parameters, Plotter
from .transcripts import find_listing, find_info
from .transcripts import TranscriptMaker
from utils import to_server_constants
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('AGG')


from matplotlib.colors import ListedColormap
from librosa.display import waveshow
import numpy as np

class Plotter:
    def __init__(self, audio, label_dict, parameters):
        plt.rc('font', **parameters.rc_font)
        self.clip_seconds = parameters.clip_seconds
        self.sample_rate = parameters.sample_rate
        self.n_xticks = parameters.n_xticks
        self.n_lists = len(label_dict)
        self.label_dict = label_dict
        self.color = parameters.color
        self.audio = audio
        self.gridspec_kw = {
            'height_ratios': [
                *(1,)*self.n_lists, 4
            ],
            'wspace':0, 'hspace':0
        }

    def __enter__(self):
        label_dict = self.label_dict
        fig, (*axes, ax1) = plt.subplots(
            1+self.n_lists, gridspec_kw=self.gridspec_kw,
            layout="constrained", figsize=(8, 3), sharex=True
        )
        cmap = ListedColormap([(0,0,0,0), 'w'])
        extent = [0, self.clip_seconds, -2, 2]
        waveshow(self.audio, sr=self.sample_rate, color=self.color, ax=ax1)
        for ax, y in zip(axes, label_dict.values()):
            ax.imshow(
                y[np.newaxis,:], cmap=cmap,
                aspect="auto", extent=extent
            )
        for ax in (*axes, ax1):
            ax.tick_params(axis='x', colors=self.color)
            ax.spines['bottom'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(length=0)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_xlabel("")
            ax.set_ylabel("")
        for ax, label in zip(axes, label_dict.keys()):
            ax.set_title(label, color=self.color)
        # Add labels to x axis
        xticks = np.linspace(0, self.clip_seconds, self.n_xticks)
        xlabels = [ f'{x:.0f} seconds' for x in xticks ]
        ax1.set_xticks(xticks, labels=xlabels)
        return fig

    def __exit__(self, *args):
        plt.close()


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
    start_time, end_time = (
        timedelta(seconds=(
            duration * (clip_id + i)
        ))
        for i in (0, 1)
    )
    end_time = min(
        end_time, start_time + timedelta(
            seconds = audio.shape[0] / samplerate
        )
    )
    label_dict = OrderedDict()
    label_dict["Automated speech timings"] = vectorize_transcript(
        transcript, timedelta(seconds=0), end_time - start_time
    )
    label_dict["Real speech timings"] = load_labels(
        label_root, figure_id, start_time, end_time
    )
    parameters = Parameters(15, 'serif')
    with Plotter(audio, label_dict, parameters) as fig: 
        return make_image(fig)


class FigureMaker:

    def __init__(self, add:set[str]):
        self.maker = TranscriptMaker(add=add)

    def __call__(self, listing: str, clip_id: int):
        info = find_info(listing)[1]
        audio_path = find_listing(listing, clip_id)
        if not audio_path.is_file():
            raise TranscriptError()
        transcript = self.maker(listing, clip_id)
        constants = to_server_constants()
        duration = info["clip_duration"]
        clip_count = info["clip_count"]
        figure_id = info["figure"]
        if clip_id >= clip_count:
            raise FigureError()
        # Sound labels and waveform
        return generate_figure(
            Path(constants["api"]["figure_root"]),
            transcript, audio_path, figure_id, clip_id, duration 
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
