"""
Main entry point for the subtitle generation system.
"""
import yaml
import logging
import argparse
from pathlib import Path
from utils import setup_logger


class SubtitlePipeline:
    def __init__(self, config_path):
        # Initialize all components
        pass

    def process_video(self, video_path):
        # Orchestrate the entire pipeline
        pass

    def handle_errors(self):
        # Global error handling
        pass


def parse_arguments():
    parser = argparse.ArgumentParser(description="Video subtitle generator")

    # Basic usage arguments
    parser.add_argument(
        "--input", "-i", help="Input video file", required=True
    )
    parser.add_argument(
        "--output", "-o", default="subtitles.srt", help="Output subtitle file"
    )

    # Advanced options
    stt_set = {"whisper", "google"}
    sound_set = {"basic", "detailed"}
    emotion_set = {"disabled", "enabled"}
    group = parser.add_argument_group("Advanced Options")
    group.add_argument(
        "--stt-engine", choices=stt_set, default="whisper",
        help="Speech-to-text engine"
    )
    group.add_argument(
        "--emotion-detection", choices=emotion_set, default="disabled",
        help="Enable emotion detection"
    )
    group.add_argument(
        "--sound-description", choices=sound_set, default="basic",
        help="Sound description level"
    )
    return parser.parse_args()


def main(config):
    # Parse arguments
    args = parse_arguments()
    L = logging.getLogger(__name__)
    # Emotion as boolean value
    use_emotion = {
        "enabled": True, "disabled": False
    }.get(args.emotion_detection, None)
    assert use_emotion in {True, False}

    # Print arguments
    L.info(f"Input: {args.input}")
    L.info(f"Output: {args.output}")
    L.info(f"STT Engine: {args.stt_engine}")
    L.info(f"Emotion Detection: {use_emotion}")
    L.info(f"Sound Description: {args.sound_description}")


if __name__ == "__main__":
    config_folder = Path('config')
    setup_logger(config_folder)
    L = logging.getLogger(__name__)
    config = None
    # Parse config file
    try:
        config = yaml.safe_load(
            open(config_folder / "config.yaml")
        )
    except FileNotFoundError:
        L.error("Missing configuration file");
        L.info(
            "Hint\ncp config/config.yaml.example config/config.yaml"
        )
    if config is not None:
        # Run pipeline
        main(config)
        L.info("Done")
    else:
        L.warning("Aborting")
