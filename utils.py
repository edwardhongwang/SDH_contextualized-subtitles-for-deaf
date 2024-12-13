"""
Utility functions and helper methods.
"""
from contextlib import redirect_stdout
from os import devnull
import yaml
import pytest
import logging
from srt import SRTParseError
import logging.config
import glob
import srt


# Logging setup
def setup_logger(config_folder=None):
    config = None
    try:
        if config_folder is not None:
            config_path = config_folder / "logging.yaml"
            config = yaml.safe_load(open(config_path))
    except FileNotFoundError:
        pass
    # Configure logging
    logging.config.dictConfig({
        "version": 1,
        "root": {
            "handlers": ["console"],
            "level": "WARNING"
        },
        "handlers": {
            "console": {
                "formatter": "full",
                "class": "logging.StreamHandler"
            }
        },
        "formatters": log_options(),
        **config
    })
    logging.root.setLevel(
        logging.getLogger().getEffectiveLevel()
    )


def log_options():
    return {
        "full": {
            "datefmt": "%Y-%m-%d_%H:%M:%S",
            "format": (
                "%(levelname)s : %(asctime)s : %(module)s : "
                "%(funcName)s : %(lineno)d -- %(message)s"
            )
        },
        "short": {
            "format": (
                "%(levelname)s : %(module)s : "
                "%(funcName)s -- %(message)s"
            )
        },
        "tiny": {
            "format": "%(levelname)s -- %(message)s"
        }
    }


def log_format(key):
    return log_options()[key]['format']


def log_date(key):
    return log_options()[key]['datefmt']


# Audio extraction
def extract_audio_from_video(video_path):
    """
    Extract audio from a video file using ffmpeg.
    The audio will have the same sample rate as the video's audio stream,
    but no higher than 16 kHz.

    Parameters:
        video_path (str): Path to the input video file.

    Returns:
        audio_path (str): Path to the output audio file.
    """
    import subprocess
    import os

    # Get directory and filename
    video_dir = os.path.dirname(video_path)
    video_filename = os.path.basename(video_path)
    video_name, _ = os.path.splitext(video_filename)

    # Output audio path
    audio_filename = f"audio_{video_name}.wav"
    audio_path = os.path.join(video_dir, audio_filename)

    # Get the sample rate of the video's audio stream
    command = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'a:0',
        '-show_entries', 'stream=sample_rate',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        video_path
    ]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    sample_rate = int(result.stdout.strip())

    # Limit the sample rate to 16 kHz
    sample_rate = min(sample_rate, 16000)

    # Build ffmpeg command
    command = [
        'ffmpeg',
        '-y',            # Overwrite output files without asking
        '-i', video_path,
        '-ac', '1',      # Mono channel
        '-ar', str(sample_rate),  # Set sample rate
        '-vn',           # No video output
        audio_path
    ]

    # Execute command
    subprocess.run(command, check=True)

    return audio_path


def silence(func):
    def wrapper():
        with redirect_stdout(open(devnull, 'w')):
            return func()
    return wrapper


@silence
def find_test_sets(test_sets=set()):

    class Find:
        def pytest_collection_modifyitems(self, items):
            nonlocal test_sets
            test_sets = test_sets.union(
                m for i in items
                for m in i.config._getini('markers')
            )

    pytest.main(
        ["--collect-only", "--assert=plain", "tests"],
        plugins=[Find()]
    )
    return sorted(test_sets)


def run_tests(test_sets):
    full_format = log_format('full')
    full_date = log_date('full')
    return pytest.main([
        "-x",  # stop at first error
        "-rA",  # print all output
        "--assert=plain",
        "--log-cli-level=INFO",
        f'--log-format={full_format}',
        f'--log-date-format={full_date}',
        "tests"
    ] + ([] if "*" in test_sets else [
        "-m", " or ".join(test_sets)
    ]))


def load_config(L, config_folder):
    # Parse config file
    try:
        return yaml.safe_load(
            open(config_folder / "config.yaml")
        )
    except FileNotFoundError:
        L.error("Missing configuration file")
        L.info(
            "Hint\ncp .env.example .env"
        )


def parse_srt(content):
    """Parses the SRT file and returns a list of subtitle entries."""
    subtitles = []

    try:
        for match in srt.parse(content):
            index = match.index 
            start_time = match.start 
            end_time = match.end 
            text = match.content 
            subtitles.append({
                'index': index,
                'start_time': start_time,
                'end_time': end_time,
                'text': text
            })
    except SRTParseError:
        return subtitles

    return subtitles


def format_srt_time(timedelta_obj):
    """Formats timedelta to SRT timestamp."""
    total_seconds = int(timedelta_obj.total_seconds())
    milliseconds = int(timedelta_obj.microseconds / 1000) + int(timedelta_obj.microseconds % 1000 > 500)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def format_srt_lines(subtitles):
    """Format the subtitles"""
    # Sort subtitles by start time
    subtitles.sort(key=lambda x: x['start_time'])
    
    # Reassign indices
    for i, subtitle in enumerate(subtitles):
        subtitle['index'] = i + 1

    for subtitle in subtitles:
        index = subtitle['index']
        start_time = format_srt_time(subtitle['start_time'])
        end_time = format_srt_time(subtitle['end_time'])
        text = subtitle['text']
        yield f"{index}\n{start_time} --> {end_time}\n{text}\n"


def format_srt(subtitles):
    return "\n".join(format_srt_lines(subtitles))
