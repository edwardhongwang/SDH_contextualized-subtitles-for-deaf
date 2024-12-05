"""
Test cases for all modules.
"""
import re
from itertools import product 
from os.path import dirname
from pathlib import Path
import srt
import yaml
import pytest
import logging
from difflib import ndiff,SequenceMatcher
from utils import setup_logger, load_config
from src import create_output_transcript_path
from src import to_described_transcript_path
from src import use_speech_to_text_engine 
from src import use_llm_proofreader
from src import use_sound_describer
from src import main 

@pytest.fixture
def min_similarity():
    return 0.75

@pytest.fixture
def min_line_ratio():
    return 0.66


def setup():
    setup_logger(Path('tests'))
    L = logging.getLogger(__name__)
    config = load_config(L, Path('config'))
    return L, config


def find_test_files(folder, filename):
    root_dir = Path(dirname(__file__)) / folder 
    input_folders = [
        folder.resolve()
        for folder in root_dir.iterdir()
        if folder.is_dir()
    ]
    in_out_pairs = []
    for folder in input_folders:
        info_path = folder / "info.yaml"
        input_path = folder / filename 
        if not input_path.exists():
            continue
        if info_path.exists():
            info = yaml.safe_load(open(info_path))
            assert 'expected' in info
            yield input_path, info


def similarity_metric(
    expected, result, min_similarity=0.5
):

    # Number of lines must be within +/- 50%
    if abs(len(result) - len(expected)) > len(expected)/2:
        return -1

    def line_line_similarity(l0, l1):
        return SequenceMatcher(None, l0, l1).ratio()

    # Most similar line each line in input
    max_similarity = {
        line: 0 for line in expected
    }
    for l0, l1 in product(max_similarity.keys(), result):
        similarity = line_line_similarity(l0, l1)
        if similarity <= max_similarity[l0]:
            continue
        max_similarity[l0] = similarity

    n_unique_lines = len(max_similarity)
    return sum(
        1 for similarity in max_similarity.values() 
        if min_similarity <= similarity
    )/n_unique_lines


@pytest.mark.fast
def test_similarity_metric():
    # 60% of lines are similar
    assert .6 == similarity_metric(
        ['00', '01', '10', 'ab', 'cd'],
        ['00', '00', '00']
    )
    # Length are too different
    assert -1 == similarity_metric(
        ['00', '01', '10', 'ab', 'cd'],
        ['00']
    )
    # 40% of lines are similar 
    assert .4 == similarity_metric(
        ['00', '01', '10', 'ab', 'cd'],
        ['xx', 'xy', 'yx', 'aa', 'cc']
    )
    # 40% of lines are identical
    assert .4 == similarity_metric(
        ['00', '01', '10', 'ab', 'cd'],
        ['ab', 'cd', 'ab', 'cd']
    )


@pytest.mark.llm
def test_openai(min_similarity, min_line_ratio):
    L, config = setup()
    for input_path, info in find_test_files("openai", "input.srt"):
        label = info.get('label', input_path)
        L.debug(f'Processing {input_path.name}: "{label}"')
        expected_text = info.get('expected', '')
        result_text = use_llm_proofreader(
            L, config, str(input_path)
        )
        expected = [
            line.content for line in srt.parse(expected_text)
        ]
        result = [
            line.content for line in srt.parse(result_text)
        ]
        metric = similarity_metric(expected, result, min_similarity)
        L.debug(
            f'{100*metric:.0f}% expected lines found with ≥'
            f'{100*min_similarity:.0f}% similarity'
        )
        if metric < min_line_ratio:
            L.error('\n'.join(ndiff(expected, result)))
            assert False
        else:
            L.debug('\n'.join(ndiff(expected, result)))


@pytest.mark.stt
@pytest.mark.fast
def test_deepgram():
    L, config = setup()
    for input_path, info in find_test_files("deepgram", "voice.mp3"):
        label = info.get('label', input_path)
        L.debug(f'Processing {input_path.name}: "{label}"')
        expected_text = info.get('expected', '')
        result_text = use_speech_to_text_engine(
            L, config, input_path, "deepgram"
        )
        expected = [
            line.content for line in srt.parse(expected_text)
        ]
        # Expect some variation with the final line
        result = [
            line.content.replace(' a Theory', ' A Theory')
            for line in srt.parse(result_text)
        ]
        result = result
        if '\n'.join(expected) != '\n'.join(result):
            L.error('\n'.join(ndiff(expected, result)))
            assert False


@pytest.mark.stt
@pytest.mark.fast
def test_groq():
    L, config = setup()
    for input_path, info in find_test_files("groq", "voice.mp3"):
        label = info.get('label', input_path)
        L.debug(f'Processing {input_path.name}: "{label}"')
        expected = info.get('expected', '')
        result = use_speech_to_text_engine(
            L, config, input_path, "groq"
        )
        if result != expected:
            print('\n'.join(ndiff(
                re.split('[.,:;\n] ?', expected),
                re.split('[.,:;\n] ?', result)
            )))
            assert False


@pytest.mark.sounds
def test_sounds(min_similarity, min_line_ratio):
    L, config = setup()
    root = "sounds"
    stt_engine = "deepgram"
    for input_path, info in find_test_files(root, "voice.mp3"):
        # Copy the input transcript from the info.yaml file
        temp_transcript_path = input_path.parent / "temp.srt"
        with open(temp_transcript_path,'w') as wf:
            wf.write(info["inputs"].get('transcript', ''))
        # Actual output transcript path
        transcript_path = to_described_transcript_path(
            temp_transcript_path
        )
        label = info.get('label', input_path)
        L.debug(f'Processing {input_path.name}: "{label}"')
        expected_text = info.get('expected', '')
        result_text = use_sound_describer(
            L, config, temp_transcript_path, input_path
        )
        expected = [
            line.content for line in srt.parse(expected_text)
        ]
        result = [
            line.content for line in srt.parse(result_text)
        ]
        metric = similarity_metric(expected, result, min_similarity)
        L.debug(
            f'{100*metric:.0f}% expected lines found with ≥'
            f'{100*min_similarity:.0f}% similarity'
        )
        if metric < min_line_ratio:
            L.error('\n'.join(ndiff(expected, result)))
            assert False
        else:
            L.debug('\n'.join(ndiff(expected, result)))

@pytest.mark.integration
def test_integration_1(min_similarity, min_line_ratio):
    L, config = setup()
    root = "integration/1"
    stt_engine = "deepgram"
    for input_path, info in find_test_files(root, "voice.mp3"):
        transcript_path = create_output_transcript_path(
            None, input_path, stt_engine
        )
        label = info.get('label', input_path)
        L.debug(f'Processing {input_path.name}: "{label}"')
        expected_text = info.get('expected', '')
        result_text = main(
            L, config, input_path, transcript_path,
            stt_engine=stt_engine, describe_sounds=False
        )
        expected = [
            line.content for line in srt.parse(expected_text)
        ]
        result = [
            line.content for line in srt.parse(result_text)
        ]
        metric = similarity_metric(expected, result, min_similarity)
        L.debug(
            f'{100*metric:.0f}% expected lines found with ≥'
            f'{100*min_similarity:.0f}% similarity'
        )
        if metric < min_line_ratio:
            L.error('\n'.join(ndiff(expected, result)))
            assert False
        else:
            L.debug('\n'.join(ndiff(expected, result)))
