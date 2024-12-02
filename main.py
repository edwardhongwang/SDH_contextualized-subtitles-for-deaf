"""
Main entry point for the subtitle generation system.
"""
import logging
import argparse
from pathlib import Path
from utils import log_format, log_date 
from utils import extract_audio_from_video
from utils import setup_logger, load_config

from src import audio_path_to_transcript_path
from src import create_output_transcript_path
from src import main
import pytest

# video_path = "data/Best Joker Scenes in The Dark Knight _ Max/Best Joker Scenes in The Dark Knight _ Max.mp4"


def parse_arguments(test_commands):
    parser = argparse.ArgumentParser(
        description="Video subtitle generator", add_help=False
    )
    subparsers = parser.add_subparsers(metavar="command", dest="command")

    # Subcommand "test"
    for cmd in test_commands:
        subparsers.add_parser(cmd, help="Run pytest")

    # Basic usage arguments
    basic_group = parser.add_argument_group("Basic Options")
    basic_group.add_argument(
        "--input", "-i", metavar="video",
        help="Input video file"
    )
    basic_group.add_argument(
        "--output", "-o", metavar="file",
        help="Output subtitle file"
    )

    # Advanced options
    stt_set = {"deepgram", "groq" }
    sound_set = {"basic", "detailed"}
    emotion_set = {"disabled", "enabled"}
    group = parser.add_argument_group("Advanced Options")
    group.add_argument(
        "--stt-engine", choices=stt_set, default="deepgram",
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
    if args.input is None:
        if args.command not in test_commands:
            parser.error("Please provide an --input video file.")

    return args


def run_main(config):
    # Parse arguments
    test_commands = "test","tests"
    args = parse_arguments(test_commands)
    L = logging.getLogger(__name__)

    # Testing
    if args.command in test_commands:
        full_format = log_format('full')
        full_date = log_date('full')
        return pytest.main([
            "-x", # stop at first error
            "-rA", # print all output
            "--assert=plain",
            "--log-cli-level=INFO",
            f'--log-format={full_format}',
            f'--log-date-format={full_date}',
            "tests"
        ])

    try:
        audio_path = ensure_audio_input(args)
    except ValueError:
        L.error(f'Issue reading {args.input}')
        return

    # Emotion as boolean value
    use_emotion = {
        "enabled": True, "disabled": False
    }.get(args.emotion_detection, None)
    assert use_emotion in {True, False}
    assert Path(audio_path).exists()

    # TODO: unused arguments
    if (use_emotion):
        L.warning(f"Ignoring Emotion Detection: {use_emotion}")
    if (args.sound_description):
        L.warning(f"Ignoring Sound Description: {args.sound_description}")

    transcript_path = create_output_transcript_path(
        args.output, audio_path, args.stt_engine
    )
    main(
        L, config, audio_path, transcript_path,
        stt_engine=args.stt_engine
    )


def ensure_audio_input(args):
    ext = Path(args.input).suffix
    audio = {'mp3'}
    return args.input if ext in audio else (
        extract_audio_from_video(args.input)
    )


if __name__ == "__main__":
    config_folder = Path('config')
    setup_logger(config_folder)
    L = logging.getLogger(__name__)
    config = load_config(L, config_folder)
    if config is not None:
        # Run pipeline
        run_main(config)
        L.info("Done")
    else:
        L.warning("Aborting")
