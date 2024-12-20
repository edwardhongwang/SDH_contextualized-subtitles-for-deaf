"""
Main entry point for the subtitle generation system.
"""
import asyncio
import logging
import argparse
from pathlib import Path
from fractions import Fraction
from server import run_servers, list_figures
from data_utils import to_server_constants
from data_utils import should_server_export
from utils import find_test_sets, run_tests
from utils import extract_audio_from_video
from utils import setup_logger, load_config

from src import audio_path_to_transcript_path
from src import create_output_transcript_path
from src import to_intersections_and_unions
from src import PlotIOU
from src import main


def float_ratio(value):
    try:
        value = float(value)
        if value < 1/100:
            raise argparse.ArgumentTypeError(f"{value:.3f} < 1/100")
        if value > 1:
            raise argparse.ArgumentTypeError(f"{value:.3f} > 1")
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value} is not a number")
    return value


def parse_arguments(L, config, test_commands):
    commands_without_input_file = (
        *test_commands, "serve", "iou"
    )
    parser = argparse.ArgumentParser(
        description="Video subtitle generator", add_help=False
    )
    subparsers = parser.add_subparsers(metavar="command", dest="command")
    # Subcommand "serve"
    serve_parser = subparsers.add_parser("serve", help="run web server")
    serve_parser.add_argument(
        "--export", action='store_true' 
    )
    # Subcommand "iou"
    figure_list = list_figures()
    figure_list_string = ", or ".join(
        f'"{listing}"' for listing in figure_list
    )
    iou_parser = subparsers.add_parser(
        "iou", help=f'Plot IOU for {figure_list_string}'
    )
    iou_parser.add_argument(
        "listing-name", metavar="dataset",
        choices=figure_list, help=figure_list_string
    )
    iou_parser.add_argument(
        "output-image", metavar="output image", type=Path,
        nargs="?", default=None, help="Output path for IOU plot"
    )
    iou_parser.add_argument(
        "--ratio", metavar="clip choice ratio", type=float_ratio,
        default="0.25", help="Ratio of chosen clips"
    )
    iou_parser.add_argument(
        "--edits", action='store_true' 
    )

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
    sound_set = {"disabled", "enabled"}
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
        "--sound-description", choices=sound_set, default="disabled",
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
        if args.command not in commands_without_input_file:
            parser.error("Please provide an --input video file.")
    else:
        if args.command in commands_without_input_file:
            parser.error(f"{args.command} has no --input option.")

    # IOU cannot support groq without edits
    if args.command == "iou" and args.stt_engine == "groq":
        if args.edits == False:
            parser.error(f"The --edits option is required for groq IOU.")

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
        should_server_export(args.export)
        constants = to_server_constants()
        asyncio.run(run_servers(
            constants.get("api", {})["port"],
            constants.get("client", {})["port"]
        ))
        return
    elif args.command == "iou":
        # Plot IOU figures
        ratio = getattr(args, "ratio")
        use_edits = getattr(args, "edits")
        stt_engine = getattr(args, "stt_engine")
        listing_name = getattr(args, "listing-name")
        frac = Fraction(ratio).limit_denominator(100)
        edit_suffix="edited" if use_edits else "plain"
        suffix=f'{stt_engine}-{edit_suffix}'
        prefix=f'iou-{listing_name}'
        png_file = getattr(args, "output-image") or Path(
            f"{prefix}-{frac.numerator}-in-{frac.denominator}-{suffix}.png"
            if ratio < 1 else f"iou-{listing_name}-complete-{suffix}.png"
        )
        clip_ids, intersections, unions = to_intersections_and_unions(
            ratio, listing_name, stt_engine, add=(
                ("edits",) if use_edits else ()
            )
        )
        iou_plot = PlotIOU(
            clip_ids, intersections, unions
        )
        with iou_plot as fig: 
            fig.savefig(
                png_file, facecolor=fig.get_facecolor()
            )
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

    # Sound descriptions as boolean value
    describe_sounds = {
        "enabled": True, "disabled": False
    }.get(args.emotion_detection, None)
    assert describe_sounds in {True, False}

    assert Path(audio_path).exists()

    # TODO: unused arguments
    if (use_emotion):
        L.warning(f"Ignoring Emotion Detection: {use_emotion}")

    transcript_path = create_output_transcript_path(
        args.output, audio_path, args.stt_engine
    )
    main(
        L, config, audio_path, transcript_path,
        stt_engine=args.stt_engine,
        describe_sounds=describe_sounds
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
