import os
import re
import srt
import base64
import subprocess
from datetime import timedelta
import json
from openai import OpenAI
from .errors import AudioExtractionError


def parse_srt(srt_file_path):
    """Parses the SRT file and returns a list of subtitle entries."""
    with open(srt_file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    subtitles = []

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
    except subprocess.CalledProcessError as e:
        raise AudioExtractionError(
            f"Error extracting audio segment: {e.stderr.decode()}"
        ) from e


def prepare_context(subtitles, current_index, n_lines):
    """Prepares previous n lines as context, without timestamps."""
    if current_index < 0:
        return ""  # No context available
    start = max(0, current_index - n_lines + 1)
    context_lines = subtitles[start:current_index + 1]
    context_text = ''
    for subtitle in context_lines:
        text = subtitle['text']
        context_text += f"{text}\n\n"
    return context_text.strip()


def run_llm(
    L, client, audio_file_path,
    audio_segment_path, context_text
):
    """Runs the LLM to analyze the audio segment."""
    # Read the audio file
    with open(audio_segment_path, 'rb') as audio_file:
        audio_data = audio_file.read()
    audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
    L.debug("Audio segment read and encoded into base64.")

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

    audio_folder = os.path.dirname(audio_file_path)
    chat_log_file_path = os.path.join(audio_folder, "chat_info.txt")

    # Write messages to chat_info.txt
    with open(chat_log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write("=== User Message ===\n")
        log_file.write(json.dumps(messages, indent=2))
        log_file.write("\n\n")

    try:
        L.debug("Sending request to OpenAI API.")
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
        with open(chat_log_file_path, 'a', encoding='utf-8') as log_file:
            log_file.write("=== Assistant Response ===\n")
            log_file.write(json.dumps(response.to_dict(), indent=2))
            log_file.write("\n\n")

        # Extract the response content
        output = response.choices[0].message.content
        L.debug("Received response from OpenAI API.")
        return output.strip()
    except Exception as e:
        L.error(f"Error calling OpenAI API: {e}")
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


def non_speech_labeling(
    L, srt_file_path, audio_file_path,
    min_gap_duration=1.5, context_lines=4
):
    # Set your OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    client = OpenAI(api_key=api_key)
    try:
        L.info("Starting processing.")
        # Parse the existing SRT file
        subtitles = parse_srt(srt_file_path)
        L.info(f"Parsed {len(subtitles)} subtitles from {srt_file_path}.")

        # Find gaps longer than min_gap_duration seconds
        gaps = find_gaps(subtitles, min_gap_duration)

        # Also consider the initial gap
        initial_gap_duration = subtitles[0]['start_time'].total_seconds()
        if initial_gap_duration > min_gap_duration:
            gaps.insert(0, {
                'start_time': timedelta(seconds=0),
                'end_time': subtitles[0]['start_time'],
                'before_index': -1  # Since there's no previous subtitle
            })
            L.info(f"Initial gap detected: {initial_gap_duration} seconds.")

        L.info(f"Found {len(gaps)} gaps longer than {min_gap_duration} seconds.")

        # Process each gap
        for gap in gaps:
            L.info(f"Processing gap from {gap['start_time']} to {gap['end_time']}.")
            # Extract audio segment
            audio_segment_path = 'temp_audio_segment.mp3'
            extract_audio_segment(
                audio_file_path,
                gap['start_time'],
                gap['end_time'],
                audio_segment_path
            )
            L.debug(f"Extracted audio segment: {audio_segment_path}")
            try:
                # Prepare context
                context_text = prepare_context(
                    subtitles, gap['before_index'], context_lines
                )

                # Run LLM
                llm_output = run_llm(
                    L, client, audio_file_path,
                    audio_segment_path, context_text
                )

                # Remove code block formatting from LLM output
                llm_output_clean = re.sub(
                    r'^```(?:json)?\n(.*?)\n```$',
                    r'\1',
                    llm_output.strip(),
                    flags=re.DOTALL
                )

                L.debug(f"LLM output (cleaned): {llm_output_clean}")

                # Check if the output indicates no significant sounds
                if llm_output_clean.strip().lower() in ['"nah"', 'nah']:
                    L.info("No significant sounds detected in this gap.")
                    continue  # No significant sounds

                try:
                    events = json.loads(llm_output_clean)
                    L.debug(f"Parsed events: {events}")

                    # Ensure events is a list of dictionaries
                    if isinstance(events, dict):
                        # If events is a dict with an 'events' key, extract it
                        if 'events' in events:
                            events = events['events']
                        else:
                            L.error(f"Unexpected dictionary format in events: {events}")
                            continue  # Skip this gap
                    elif isinstance(events, list):
                        # Verify that each item in the list is a dictionary
                        if not all(isinstance(event, dict) for event in events):
                            L.error(f"Events list contains non-dictionary items: {events}")
                            continue  # Skip this gap
                    else:
                        L.error(f"Unexpected events type: {type(events)}")
                        continue  # Skip this gap

                    L.info(f"Detected {len(events)} event(s) in gap.")
                    # Adjust timestamps
                    adjusted_events = adjust_timestamps(events, gap['start_time'])
                    # Insert events into subtitles
                    insert_events_into_srt(subtitles, adjusted_events, gap['before_index'])
                except json.JSONDecodeError:
                    L.error(f"Invalid JSON output from LLM: {llm_output_clean}")
                    continue  # Skip this gap

            finally:
                # Clean up temporary audio file
                if os.path.exists(audio_segment_path):
                    os.remove(audio_segment_path)
                    L.debug("Temporary audio segment deleted.")

        # Save the updated SRT file
        return "\n".join(format_srt_lines(subtitles))

    except Exception as e:
        L.error(f"Error processing files: {e}")
        raise
