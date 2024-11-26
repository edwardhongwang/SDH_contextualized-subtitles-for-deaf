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
│   ├── preprocessor.py       # Media preprocessing
│   ├── speech_to_text.py     # Speech transcription
│   ├── subtitle_format.py    # Subtitle formatting
│   ├── emotion_context.py    # Emotion analysis
│   ├── sound_description.py  # Non-speech sounds
│   └── subtitle_generator.py # Final generation
├── tests/
│   ├── test_data/           # Test files
│   └── test_modules.py      # Test cases
├── utils.py                 # Utilities
└── main.py                 # Entry point
```

## Prerequisites

- Python 3.8+
- FFmpeg (for media processing)
- Required Python packages:
  ```
  pip install -r requirements.txt
  ```

- API Keys (add to config/config.yaml):
  - Google Cloud Speech-to-Text API
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
   cp config/config.yaml.example config/config.yaml
   # Edit config.yaml with your API keys
   ```

## Usage

### Basic Usage

```bash
python main.py --input video.mp4 --output subtitles.srt
```

### Advanced Options

```bash
python main.py --input video.mp4 \
               --output subtitles.srt \
               --stt-engine whisper \
               --emotion-detection enabled \
               --sound-description detailed
```

### Configuration Options

Edit `config/config.yaml` to customize:
- STT engine preferences
- Emotion detection sensitivity
- Sound description detail level
- Output format settings

Example configuration:
```yaml
stt:
  primary_engine: "google"
  confidence_threshold: 0.85

emotion:
  detection_enabled: true
  intensity_threshold: 0.6

sound:
  description_detail: "detailed"
  min_volume_threshold: -30
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
python -m pytest tests/test_modules.py
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
- Multiple la