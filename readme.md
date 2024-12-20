# Contextualized Subtitle Generator

A comprehensive tool that generates context-rich subtitles for deaf and hard-of-hearing viewers, incorporating speech transcription, emotional context, and non-speech sound descriptions.

## Features

- **Accurate Speech Transcription**
  - Multiple STT engine support (Google Speech-to-Text, OpenAI Whisper)
  - Speaker diarization and identification
  - High accuracy with confidence score validation

- **Intelligent Subtitle Formatting**
  - Natural language segmentation
  - Proper line breaks and timing
  - Speaker attribution

- **Emotional Context Enhancement**
  - Speech emotion detection
  - Tone analysis
  - Visual formatting based on emotional intensity
  - Support for 7 emotion categories: happy, sad, angry, neutral, fear, disgust, surprise

- **Non-Speech Sound Description**
  - Automatic detection of significant sound events
  - Context-aware sound descriptions
  - Visual frame analysis for better context
  - Integration with speech subtitles

## Project Structure

```
contextualized-subtitles/
├── config/
│   └── config.yaml           # Configuration settings
├── src/
├── tests/
│   ├── groq/
│   ├── openai/
│   ├── deepgram/
│   ├── integration/
│   └── test_modules.py      # Test cases
├── utils.py                 # Utilities
└── main.py                  # Entry point
└── .env                     # API keys
```

## Prerequisites

- Python ~= 3.10.12
- FFmpeg ~= 6.1 (for media processing)
- Required Python packages:
  ```
  pip install -r requirements.txt
  ```

- API Keys (add to .env):
  - Google Cloud Speech-to-Text API
  - Deepgram Speech-to-Text API
  - Groq Speech-to-Text API
  - OpenAI API (for Whisper)
  - Any additional APIs for emotion detection

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/contextualized-subtitles.git
   cd contextualized-subtitles
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure API keys:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Usage

### Basic Usage

```bash
python main.py --input video.mp4 --output subtitles.srt
```

```bash
python main.py --input audio.mp3 --output subtitles.srt
```

### Running Webserver

```bash
python main.py serve
```

or

```bash
python main.py serve --export
```

### Creating IOU plots

```bash
python main.py iou ansari 
```

or

```bash
python main.py iou fox
```

### Running Tests

List all categories of tests

```bash
python main.py test -h
```

Run certain tests, example "llm":

```
python main.py test llm 
```

```
python main.py test llm 
```

Run all tests

```
python main.py tests
```

### Advanced Options

```bash
python main.py --input video.mp4 \
               --output subtitles.srt \
               --stt-engine groq \
               --emotion-detection enabled \
               --sound-description enabled 
```

### Configuration Options

Edit `config/config.yaml` to customize:
- STT engine preferences
- Emotion detection sensitivity
- Sound description detail level
- Output format settings

Example configuration:
```yaml
deepgram:
  model: nova-2

openai:
  model: o1-mini

groq:
  temperature: 0
  model: distil-whisper-large-v3-en

stt:
  primary_engine: "deepgram"

# TODO
emotion:
  detection_enabled: true
  intensity_threshold: 0.6

sounds:
  min_gap_duration: 1.5 
  context_lines: 4
```

## Output Format

The generator produces subtitles in standard SRT format with enhanced context:

```
1
00:00:01,000 --> 00:00:04,000
[John, happy] That's amazing news!

2
00:00:04,500 --> 00:00:06,000
[dramatic music plays]

3
00:00:06,500 --> 00:00:09,000
[Sarah, sad] I wish I could have been there...
```

## Development

### Running Tests

```bash
python main.py test
```

### Adding New Features

1. For new STT engines:
   - Add engine implementation in speech_to_text.py
   - Update configuration template

2. For new emotion categories:
   - Add detection in emotion_context.py
   - Update formatting rules

## Performance Considerations

- Processing time varies based on:
  - Video length
  - Enabled features
  - Selected STT engine
  - Sound description detail level

- Recommended specs:
  - 16GB+ RAM
  - Modern multi-core CPU
  - GPU (optional, for faster processing)

## Error Handling

The system includes comprehensive error handling:
- Input validation
- API failure recovery
- Processing error logging
- Output validation

Logs are stored in `logs/` directory with detailed error information.

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Speech-to-Text API
- OpenAI Whisper
- SpeechBrain project
- FFmpeg project

## Support

For support and questions:
- Open an issue
- Check the [Wiki](wiki-link)
- Contact: your-email@example.com

## Roadmap

Future improvements planned:
- Additional STT engine support
- Enhanced emotion detection
- Real-time processing capability
