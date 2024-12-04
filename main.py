"""
Main entry point for the subtitle generation system.
"""
import asyncio
import logging
import argparse
from pathlib import Path
from src import run_servers
from utils import to_server_constants
from utils import find_test_sets, run_tests
from utils import extract_audio_from_video
from utils import setup_logger, load_config

from src import audio_path_to_transcript_path
from src import create_output_transcript_path
from src import main


def parse_arguments(L, config, test_commands):
    parser = argparse.ArgumentParser(
        description="Video subtitle generator", add_help=False
    )
    subparsers = parser.add_subparsers(metavar="command", dest="command")
    subparsers.add_parser("serve", help="run web server")

    # Subcommand "test"
    test_list = find_test_sets()
    for cmd in test_commands:
        test_str = ", ".join(test_list)
        subparsers.add_parser(cmd, help=test_str).add_argument(
            "test_sets", metavar="test sets", nargs='*', default="*",
            choices=test_list+["*"], help=test_str
        )

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
    stt_set = {"deepgram", "groq"}
    sound_set = {"basic", "detailed"}
    emotion_set = {"disabled", "enabled"}
    stt_default_default = "deepgram"
    stt_default = config.get('stt', {})['primary_engine']
    group = parser.add_argument_group("Advanced Options")
    group.add_argument(
        "--stt-engine", choices=stt_set, default=stt_default,
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

    # Ensure valid STT engine
    if stt_default not in stt_set:
        L.warning(
            f'Unknown stt engine "{stt_default}" found in config. '
            f'Defaulting instead to "{stt_default_default}"'
        )
        stt_default = stt_default_default

    # Require input iff not testing
    if args.input is None:
        if args.command not in (*test_commands, "serve"):
            parser.error("Please provide an --input video file.")

    return args


def run_main(config):
    # Parse arguments
    test_commands = "test", "tests"
    L = logging.getLogger(__name__)
    args = parse_arguments(L, config, test_commands)

    if args.command in test_commands:
        # Run tests
        return run_tests(args.test_sets)
    elif args.command == "serve":
        # Run web servers
        constants = to_server_constants()
        asyncio.run(run_servers(
            constants.get("api", {})["port"],
            constants.get("client", {})["port"]
        ))
        return
    # Otherwise, continue with pipeline
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
    audio = {'.mp3', '.wav'}
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
