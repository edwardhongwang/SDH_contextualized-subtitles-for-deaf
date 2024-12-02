"""
Utility functions and helper methods.
"""
import yaml
import logging
import logging.config
import glob


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
