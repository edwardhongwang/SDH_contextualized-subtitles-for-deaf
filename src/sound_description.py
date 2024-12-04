import os
import re
import subprocess
from datetime import timedelta
import json
from openai import OpenAI
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set your OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Please set the OPENAI_API_KEY environment variable")
client = OpenAI(api_key=api_key)

# Paths to your files
SRT_FILE_PATH = 'data/Best Joker Scenes in The Dark Knight _ Max/proofread_transcript_nova-2_audio_Best Joker Scenes in The Dark Knight _ Max.srt'
AUDIO_FILE_PATH = 'data/Best Joker Scenes in The Dark Knight _ Max/audio_Best Joker Scenes in The Dark Knight _ Max.wav'

# Define the path to chat_info.txt
audio_folder = os.path.dirname(AUDIO_FILE_PATH)
CHAT_LOG_FILE_PATH = os.path.join(audio_folder, "chat_info.txt")

# Create the output SRT file path
srt_folder = os.path.dirname(SRT_FILE_PATH)
srt_filename = os.path.basename(SRT_FILE_PATH)
OUTPUT_SRT_FILE_PATH = os.path.join(srt_folder, f"description_{srt_filename}")

# Constants
MIN_GAP_DURATION = 1.5  # seconds
CONTEXT_LINES = 4      # Number of previous lines for context

def parse_srt(srt_file_path):
    """Parses the SRT file and returns a list of subtitle entries."""
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    pattern = r'(\d+)\n([\d:,]+) --> ([\d:,]+)\n(.*?)\n\n'
    matches = re.findall(pattern, content, re.DOTALL)
    subtitles = []

    for match in matches:
        index = int(match[0])
        start_time = parse_srt_time(match[1])
        end_time = parse_srt_time(match[2])
        text = match[3].strip()
        subtitles.append({
            'index': index,
            'start_time': start_time,
            'end_time': end_time,
            'text': text
        })

    return subtitles

def parse_srt_time(time_str):
    """Converts SRT timestamp to timedelta."""
    hours, minutes, seconds = time_str.split(':')
    seconds, milliseconds = seconds.split(',')
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(milliseconds)
    )

def format_srt_time(timedelta_obj):
    """Formats timedelta to SRT timestamp."""
    total_seconds = int(timedelta_obj.total_seconds())
    milliseconds = int(timedelta_obj.microseconds / 1000) + int(timedelta_obj.microseconds % 1000 > 500)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

def find_gaps(subtitles, min_gap_duration):
    """Finds gaps longer than min_gap_duration between subtitles."""
    gaps = []
    for i in range(len(subtitles) - 1):
        current_end = subtitles[i]['end_time']
        next_start = subtitles[i + 1]['start_time']
        gap_duration = (next_start - current_end).total_seconds()
        if gap_duration > min_gap_duration:
            gaps.append({
                'start_time': current_end,
                'end_time': next_start,
                'before_index': i
            })
    return gaps

def extract_audio_segment(audio_file_path, start_time, end_time, output_path):
    """Extracts an audio segment using FFmpeg."""
    try:
        start_str = str(start_time.total_seconds())
        duration = end_time - start_time
        duration_str = str(duration.total_seconds())
        command = [
            'ffmpeg', '-y',
            '-ss', start_str,
            '-t', duration_str,
            '-i', audio_file_path,
            '-c:a', 'libmp3lame',
            output_path
        ]
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logging.debug(f"Extracted audio segment: {output_path}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error extracting audio segment: {e.stderr.decode()}")
        raise

def prepare_context(subtitles, current_index):
    """Prepares the previous CONTEXT_LINES lines as context, without timestamps."""
    if current_index < 0:
        return ""  # No context available
    start = max(0, current_index - CONTEXT_LINES + 1)
    context_lines = subtitles[start:current_index + 1]
    context_text = ''
    for subtitle in context_lines:
        text = subtitle['text']
        context_text += f"{text}\n\n"
    return context_text.strip()

def run_llm(audio_segment_path, context_text):
    import base64
    """Runs the LLM to analyze the audio segment."""
    # Read the audio file
    with open(audio_segment_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
    logging.debug("Audio segment read and encoded into base64.")

    # Prepare the messages payload
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"""
    You will analyze a provided audio segment and its context to identify significant non-speech audio events. For each event, you need to:

    1. **Provide precise timestamps:**
    - "start_timestamp": Relative start time within the segment, in the format `HH:MM:SS,mmm`.
    - "end_timestamp": Relative end time within the segment, in the same format.
    - Timestamps should be precise to milliseconds.

    2. **Ensure no time overlaps:**
    - If multiple events occur, their timeframes should not overlap.
    - Events should be sequential and non-overlapping within the segment.

    3. **Write concise descriptions:**
    - "description": A brief description of the sound, using no more than 5 words or 10 tokens.

    4. **Handle cases with no significant sounds:**
    - If no significant non-speech sounds are present, output `"nah"`.

    **Output Format:**
    - Provide the results as a JSON array of objects, each representing one event.
    - Each object should have the keys:
    - "start_timestamp"
    - "end_timestamp"
    - "description"
    - The "start_timestamp" and "end_timestamp" are relative to the start of the audio segment, which is always `00:00:00,000`. 
    - Ensure that the timestamps are precise to milliseconds (`HH:MM:SS,mmm`).
    - Make sure that the time intervals of events do not overlap.
    - Use the context provided (previous lines from the SRT file) to inform your descriptions.
    - do not hallucinate, do not make up things, only describe what you hear
    - Do not include any code block formatting or markdown in your response.**
    - If there are no significant sounds, simply output: "nah"

    **Examples:**

    *If significant sounds are present:*

    [
    {{
        "start_timestamp": "00:00:01,500",
        "end_timestamp": "00:00:03,000",
        "description": "door slams"
    }},
    {{
        "start_timestamp": "00:00:04,500",
        "end_timestamp": "00:00:05,000",
        "description": "glass shatters"
    }}
    ]

    *If no significant sounds are present:*

    "nah"

    here is the past few lines of the transcript for context:
    {context_text}
    """
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": audio_data_base64,
                        "format": "mp3"
                    }
                }
            ]
        }
    ]

    # Write messages to chat_info.txt
    with open(CHAT_LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
        log_file.write("=== User Message ===\n")
        log_file.write(json.dumps(messages, indent=2))
        log_file.write("\n\n")

    try:
        logging.debug("Sending request to OpenAI API.")
        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o-audio-preview-2024-10-01",
            messages=messages,
            modalities=["text"],
            temperature=0.2,
            max_tokens=2048,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        # Write response to chat_info.txt
        with open(CHAT_LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
            log_file.write("=== Assistant Response ===\n")
            log_file.write(json.dumps(response.to_dict(), indent=2))
            log_file.write("\n\n")

        # Extract the response content
        output = response.choices[0].message.content
        logging.debug("Received response from OpenAI API.")
        return output.strip()
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return "nah"  # Return "nah" on error as a safe default

def adjust_timestamps(events, gap_start_time):
    """Adjusts event timestamps relative to the entire audio."""
    adjusted_events = []
    for event in events:
        event_start = parse_srt_time(event['start_timestamp'])
        event_end = parse_srt_time(event['end_timestamp'])
        absolute_start = gap_start_time + event_start
        absolute_end = gap_start_time + event_end
        adjusted_event = {
            'start_time': absolute_start,
            'end_time': absolute_end,
            'description': event['description']
        }
        adjusted_events.append(adjusted_event)
    return adjusted_events

def insert_events_into_srt(subtitles, events, before_index):
    """Inserts new events into the subtitles list."""
    index = subtitles[-1]['index'] + 1 if subtitles else 1
    insertion_point = before_index + 1 if before_index >= 0 else 0
    for event in events:
        new_entry = {
            'index': index,
            'start_time': event['start_time'],
            'end_time': event['end_time'],
            'text': f"[{event['description']}]"
        }
        subtitles.insert(insertion_point, new_entry)
        insertion_point += 1
        index += 1

def save_srt(subtitles, output_srt_file_path):
    """Saves the subtitles list to an SRT file."""
    # Sort subtitles by start time
    subtitles.sort(key=lambda x: x['start_time'])
    
    # Reassign indices
    for i, subtitle in enumerate(subtitles):
        subtitle['index'] = i + 1

    with open(output_srt_file_path, 'w', encoding='utf-8') as file:
        for subtitle in subtitles:
            index = subtitle['index']
            start_time = format_srt_time(subtitle['start_time'])
            end_time = format_srt_time(subtitle['end_time'])
            text = subtitle['text']
            file.write(f"{index}\n{start_time} --> {end_time}\n{text}\n\n")

def non_speech_labeling():
    try:
        logging.info("Starting processing.")
        # Parse the existing SRT file
        subtitles = parse_srt(SRT_FILE_PATH)
        logging.info(f"Parsed {len(subtitles)} subtitles from {SRT_FILE_PATH}.")

        # Find gaps longer than MIN_GAP_DURATION seconds
        gaps = find_gaps(subtitles, MIN_GAP_DURATION)

        # Also consider the initial gap
        initial_gap_duration = subtitles[0]['start_time'].total_seconds()
        if initial_gap_duration > MIN_GAP_DURATION:
            gaps.insert(0, {
                'start_time': timedelta(seconds=0),
                'end_time': subtitles[0]['start_time'],
                'before_index': -1  # Since there's no previous subtitle
            })
            logging.info(f"Initial gap detected: {initial_gap_duration} seconds.")

        logging.info(f"Found {len(gaps)} gaps longer than {MIN_GAP_DURATION} seconds.")

        # Process each gap
        for gap in gaps:
            logging.info(f"Processing gap from {gap['start_time']} to {gap['end_time']}.")
            # Extract audio segment
            audio_segment_path = 'temp_audio_segment.mp3'
            try:
                extract_audio_segment(
                    AUDIO_FILE_PATH,
                    gap['start_time'],
                    gap['end_time'],
                    audio_segment_path
                )

                # Prepare context
                context_text = prepare_context(subtitles, gap['before_index'])

                # Run LLM
                llm_output = run_llm(audio_segment_path, context_text)

                # Remove code block formatting from LLM output
                llm_output_clean = re.sub(
                    r'^```(?:json)?\n(.*?)\n```$',
                    r'\1',
                    llm_output.strip(),
                    flags=re.DOTALL
                )

                logging.debug(f"LLM output (cleaned): {llm_output_clean}")

                # Check if the output indicates no significant sounds
                if llm_output_clean.strip().lower() in ['"nah"', 'nah']:
                    logging.info("No significant sounds detected in this gap.")
                    continue  # No significant sounds

                try:
                    events = json.loads(llm_output_clean)
                    logging.debug(f"Parsed events: {events}")

                    # Ensure events is a list of dictionaries
                    if isinstance(events, dict):
                        # If events is a dict with an 'events' key, extract it
                        if 'events' in events:
                            events = events['events']
                        else:
                            logging.error(f"Unexpected dictionary format in events: {events}")
                            continue  # Skip this gap
                    elif isinstance(events, list):
                        # Verify that each item in the list is a dictionary
                        if not all(isinstance(event, dict) for event in events):
                            logging.error(f"Events list contains non-dictionary items: {events}")
                            continue  # Skip this gap
                    else:
                        logging.error(f"Unexpected events type: {type(events)}")
                        continue  # Skip this gap

                    logging.info(f"Detected {len(events)} event(s) in gap.")
                    # Adjust timestamps
                    adjusted_events = adjust_timestamps(events, gap['start_time'])
                    # Insert events into subtitles
                    insert_events_into_srt(subtitles, adjusted_events, gap['before_index'])
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON output from LLM: {llm_output_clean}")
                    continue  # Skip this gap

            finally:
                # Clean up temporary audio file
                if os.path.exists(audio_segment_path):
                    os.remove(audio_segment_path)
                    logging.debug("Temporary audio segment deleted.")

        # Save the updated SRT file
        save_srt(subtitles, OUTPUT_SRT_FILE_PATH)
        logging.info(f"Updated SRT file saved to {OUTPUT_SRT_FILE_PATH}")

    except Exception as e:
        logging.error(f"Error processing files: {e}")
        raise

if __name__ == '__main__':
    non_speech_labeling()
