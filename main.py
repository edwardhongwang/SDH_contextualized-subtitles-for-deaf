"""
Main entry point for the subtitle generation system.
"""
import yaml
import logging
import argparse
from pathlib import Path
from utils import setup_logger
from tests import test_speech_to_text


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
    parser = argparse.ArgumentParser(
        description="Video subtitle generator", add_help=False
    )
    subparsers = parser.add_subparsers(metavar="command", dest="command")

    # Subcommand "test"
    test_parser = subparsers.add_parser("test", help="Test speech to text")

    # Basic usage arguments
    basic_group = parser.add_argument_group("Basic Options")
    basic_group.add_argument(
        "--input", "-i", metavar="video",
        help="Input video file"
    )
    basic_group.add_argument(
        "--output", "-o", default="subtitles.srt", metavar="file",
        help="Output subtitle file"
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
    group.add_argument("--help", "-h", action="help")
    args = parser.parse_args()

    # Require input iff not testing
    if args.command != "test" and args.input is None:
        parser.error("Please provide an --input video file.")

    return args


def main(config):
    # Parse arguments
    args = parse_arguments()
    L = logging.getLogger(__name__)

    # Testing placeholder
    if args.command == "test":
        return test_speech_to_text(L)

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
