import logging
from tvsm_extractor import load_labels, vectorize_transcript 
from matplotlib import pyplot as plt
from .main import use_speech_to_text_engine 
from utils import load_config, parse_srt
from data_utils import find_audio_file, find_listing_info
from data_utils import find_figure_label_folder
from fractions import Fraction
from datetime import timedelta
from pathlib import Path
from random import sample
import numpy as np


class ParametersForIOU:

    def __init__(self, font_size, family):
        self.colors = (
            'w', 'xkcd:sky blue', 'xkcd:sky blue'
        )
        self.rc_font = {
            'size': font_size, 'family': family
        }

def to_intersections_and_unions(
    choice_ratio, listing, add=()
):
    info = find_listing_info(listing)
    figure_id = info["figure"]
    clip_count = info["clip_count"]
    clip_duration = info["clip_duration"]
    n_chosen = round(clip_count * choice_ratio)
    clip_ids = sorted(sample(
        list(range(clip_count)), n_chosen
    ))
    intersections, unions = list(zip(*[
        to_intersection_and_union(
            listing, clip_id, figure_id, clip_duration, add
        )
        for clip_id in clip_ids
    ]))
    return clip_ids, intersections, unions


def to_intersection_and_union(
    listing, clip_id, figure_id, clip_duration, add
):
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    audio_path = find_audio_file(listing, clip_id)
    transcript = use_speech_to_text_engine(
        L, config, audio_path, stt_engine="deepgram"
    )
    if transcript is None:
        L.warning(f'Skipping clip {clip_id} of "{listing}"')
        return 0, 0
    start_time = timedelta(seconds=clip_duration * clip_id)
    duration_time = timedelta(seconds=clip_duration)
    end_time = start_time + duration_time
    truth = load_labels(
        find_figure_label_folder(), figure_id,
        start_time, end_time
    )
    automated = vectorize_transcript(
        parse_srt(transcript), timedelta(seconds=0),
        duration_time 
    )
    # The vectorized transcripts are in milliseconds
    intersections = np.sum(truth & automated) / 1000 
    unions = np.sum(truth | automated) / 1000 
    return intersections, unions


def iou(intersections, unions):
    i = np.array(intersections, dtype=np.float32)
    u = np.array(unions, dtype=np.float32)
    return np.where(u != 0, i / u, 0)


class PlotIOU:
    def __init__(
        self, clip_ids, intersections, unions
    ):
        parameters = ParametersForIOU(15, "serif")
        plt.rc('font', **parameters.rc_font)
        self.colors = parameters.colors
        self.n_y_steps = 5
        self.clip_ids = clip_ids
        self.intersections = intersections
        self.unions = unions
        self.gridspec_kw = {
            'height_ratios': [1,1],
            'wspace':0, 'hspace':0
        }

    def __enter__(self):
        fig, (ax0,ax1) = plt.subplots(
            2, gridspec_kw=self.gridspec_kw,
            layout="constrained", figsize=(8, 8), sharex=False
        )
        background_color = 3 * (1/10,)
        fig.patch.set_facecolor(background_color)
        clip_ids = self.clip_ids
        intersections = self.intersections
        unions = self.unions
        iou_vals = iou(
            intersections, unions
        )
        n_clips = len(clip_ids)
        mean_iou = np.mean(iou_vals)
        width = 0.8
        thickness = (1/20) * (
            max(iou_vals) - min(iou_vals)
        )
        ax0.bar(
            clip_ids, [thickness]*n_clips, width, label="IoU",
            bottom=iou_vals-thickness, align="center",
            color=self.colors[2]
        )
        ax0.axhline(
            y=mean_iou+thickness/2, color=self.colors[2],
            xmin=0, xmax=clip_ids[-1]+1
        )
        ax1.bar(
            [x-0.1 for x in clip_ids], unions, width, label="Union",
            bottom=0, align="center", color=self.colors[0]
        )
        ax1.bar(
            clip_ids, intersections, width, label="Intersection",
            bottom=0, align="center", color=self.colors[1]
        )
        for ax in [ax0, ax1]:
            ax.set_facecolor(background_color)
            ax.tick_params(axis='x', colors=self.colors[0])
            ax.spines['bottom'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.tick_params(length=0)
            ax.set_xlabel("")
            # Add labels to x axis
            clip_ticks = clip_ids[
                ::round(max(1, len(clip_ids))/4)
            ] 
            clip_labels = [ f'clip #{round(x)}' for x in clip_ticks ]
            ax.set_xticks(clip_ticks, labels=clip_labels)
        # Intersection over Union plot
        ax0.set_title(
            f"Intersection / Union = {mean_iou:.3f} over {n_clips} clips",
            color=self.colors[0]
        )
        ax0.set_ylabel("Ratio", color=self.colors[0])
        ax0.spines['bottom'].set_visible(True)
        ax0.spines['bottom'].set_color(self.colors[0])
        ax0.set_ylim(0, 1)
        ax0_yticks = np.linspace(0, 1, self.n_y_steps)
        ax0_ylabels = ["0"] + [
            '$\\frac{'+f'{Fraction(r).numerator}'+'}{'\
            f'{Fraction(r).denominator}'+'}$'
            for r in ax0_yticks[1:-1]
        ] + ["1"]
        ax0.set_yticks(ax0_yticks, ax0_ylabels, color=self.colors[0])
        ax0.legend(
            loc="lower right", facecolor=[0,0,0,1/2], edgecolor="k",
            labelcolor="w"
        )
        # Intersection and Union plot
        ax1.set_title(
            "Automated vs. Real: Intersection and Union",
            color=self.colors[0]
        )
        ax1.set_ylabel("Total time in seconds", color=self.colors[0])
        ax1_yticks = np.linspace(0, np.max(unions), self.n_y_steps)
        ax1_ylabels = [
            f"{round(seconds)}s" for seconds in ax1_yticks
        ]
        ax1.set_yticks(ax1_yticks, ax1_ylabels, color=self.colors[0])
        ax1.legend(
            loc="lower right", facecolor=[0,0,0,1/2], edgecolor="k",
            labelcolor="w"
        )
        return fig

    def __exit__(self, *args):
        plt.close()
