import os
import subprocess
import pysubs2
import shlex
import base64

from google import genai
from google.genai import types

def get_emotion_label(video_path: str, transcript_line: str, client, model: str) -> str:
    """
    Send the video clip and transcript line to Gemini (Google GenAI) for emotion analysis.
    Expect a short textual emotion response.
    """

    # Read the video segment bytes
    with open(video_path, "rb") as vf:
        video_bytes = vf.read()

    # Prepare the prompt
    prompt_text = (
        "What is the predominant emotion expressed in the following line of dialogue?\n"
        "Respond with only one or two words.\n\n"
        f"Line: \"{transcript_line}\""
    )

    video_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
    text_part = types.Part.from_text(prompt_text)

    contents = [
        types.Content(
            role="user",
            parts=[video_part, text_part]
        )
    ]

    # No JSON schema or MIME type to avoid JSON parsing issues
    generate_content_config = types.GenerateContentConfig(
        temperature=0.1,
        top_p=0.95,
        max_output_tokens=8192,
        response_modalities=["TEXT"],
        safety_settings=[
            types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="OFF"),
            types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="OFF")
        ]
    )

    response_text = ""
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config
    ):
        # Just accumulate text
        if hasattr(chunk, 'text'):
            response_text += chunk.text

    # Process the response_text to extract 1-2 words
    response_text = response_text.strip()
    words = response_text.split()
    if len(words) > 2:
        response_text = " ".join(words[:2])
    if not response_text:
        response_text = "neutral"

    return response_text

def extract_video_segment(input_video: str, start_ms: int, end_ms: int, output_path: str):
    duration_ms = end_ms - start_ms
    start_sec = start_ms / 1000.0
    duration_sec = duration_ms / 1000.0

    cmd = f'ffmpeg -y -ss {start_sec} -i {shlex.quote(input_video)} -t {duration_sec} -c copy {shlex.quote(output_path)}'
    subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def main(srt_path: str, video_path: str):
    # Load subtitles
    subs = pysubs2.load(srt_path)

    # Prepare output filename
    dir_name = os.path.dirname(srt_path)
    base_name = os.path.basename(srt_path)
    new_filename = os.path.join(dir_name, "emotion_" + base_name)

    # Temporary directory for video segments
    temp_dir = os.path.join(dir_name, "temp_segments")
    os.makedirs(temp_dir, exist_ok=True)

    # Initialize the GenAI client
    client = genai.Client(
        vertexai=True,
        project="sdh-class-project",
        location="us-central1"
    )

    model_name = "gemini-1.5-flash-002"

    # Process each line in the SRT
    for i, line in enumerate(subs):
        text = line.text.strip()
        word_count = len(text.split())

        if word_count > 3:
            start_ms = line.start
            end_ms = line.end
            segment_path = os.path.join(temp_dir, f"segment_{i}.mp4")

            try:
                extract_video_segment(video_path, start_ms, end_ms, segment_path)
            except subprocess.CalledProcessError as e:
                print(f"Error extracting segment for line {i}: {e}")
                continue

            emotion_label = get_emotion_label(segment_path, text, client, model_name)
            line.text = f"{text} ({emotion_label})"

            if os.path.exists(segment_path):
                os.remove(segment_path)
        else:
            # No emotion analysis for short lines
            pass

    subs.save(new_filename, encoding="utf-8")

    # Attempt to clean up temp directory if empty
    try:
        os.rmdir(temp_dir)
    except OSError:
        pass

    print(f"Emotion-labeled SRT saved to {new_filename}")

if __name__ == "__main__":
    srt_input = "data/Best Joker Scenes in The Dark Knight _ Max/proofread_transcript_nova-2_audio_Best Joker Scenes in The Dark Knight _ Max.srt"
    video_input = "data/Best Joker Scenes in The Dark Knight _ Max/Best Joker Scenes in The Dark Knight _ Max.mp4"
    main(srt_input, video_input)
