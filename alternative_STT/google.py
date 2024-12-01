#Google Speech to Text batch v1
import os
from google.cloud import storage
from google.cloud import speech_v1
from pydub import AudioSegment

bucket_name = "cynthiastt"

def convert_to_mono(input_path):
    """Convert stereo audio to mono and ensure correct format."""
    print(f"Converting {os.path.basename(input_path)} to mono...")
    
    # Load audio file
    audio = AudioSegment.from_wav(input_path)
    
    # Convert to mono
    mono_audio = audio.set_channels(1)
    
    # Create temporary file path
    base_path = os.path.splitext(input_path)[0]
    mono_path = f"{base_path}_mono.wav"
    
    # Export mono audio
    mono_audio.export(mono_path, format="wav")
    print(f"Created mono version at: {mono_path}")
    
    return mono_path

def upload_to_gcs(local_file_path, bucket_name):
    """Upload a file to Google Cloud Storage."""
    try:
        print(f"Uploading {os.path.basename(local_file_path)} to GCS bucket {bucket_name}...")
        storage_client = storage.Client()
        
        # Check if bucket exists, if not create it
        try:
            bucket = storage_client.get_bucket(bucket_name)
        except Exception:
            bucket = storage_client.create_bucket(bucket_name)
            print(f"Created new bucket: {bucket_name}")
        
        blob_name = os.path.basename(local_file_path)
        blob = bucket.blob(blob_name)
        blob.upload_from_filename(local_file_path)
        gcs_uri = f"gs://{bucket_name}/{blob_name}"
        print(f"Successfully uploaded to {gcs_uri}")
        return gcs_uri
    except Exception as e:
        print(f"Error uploading to GCS: {str(e)}")
        raise

def transcribe_audio_with_timestamps(local_file_path):
    """Transcribe audio file with word-level timestamps."""
    # Convert to mono first
    mono_path = convert_to_mono(local_file_path)
    
    # Upload mono version to GCS
    gcs_uri = upload_to_gcs(mono_path, bucket_name)
    
    # Initialize Speech client
    client = speech_v1.SpeechClient()

    # Configure recognition
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
        enable_word_time_offsets=True  # Enable word timestamps
    )

    audio = speech_v1.RecognitionAudio(uri=gcs_uri)

    print("\nStarting transcription with timestamps...")
    operation = client.long_running_recognize(config=config, audio=audio)
    
    print("Waiting for operation to complete... This may take several minutes.")
    response = operation.result(timeout=None)

    # Process results
    transcripts = []
    print("\nProcessing transcription results...")
    
    try:
        for result in response.results:
            alternative = result.alternatives[0]
            transcript_with_timestamps = []
            
            # Add the full transcript
            transcript_with_timestamps.append(f"\nTranscript: {alternative.transcript}")
            transcript_with_timestamps.append(f"Confidence: {alternative.confidence:.2f}")
            
            # Add sentence-level timestamps
            transcript_with_timestamps.append("\nSentence-level timestamps:")
            # Get first word's start time and last word's end time
            first_word = alternative.words[0]
            last_word = alternative.words[-1]
            start_time = first_word.start_time.total_seconds()
            end_time = last_word.end_time.total_seconds()
            
            # Convert to the format HH:MM:SS,mmm
            def format_timestamp(seconds):
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                seconds = seconds % 60
                milliseconds = int((seconds % 1) * 1000)
                seconds = int(seconds)
                return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
            
            transcript_with_timestamps.append(
                f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}\n{alternative.transcript}"
            )
            
            transcripts.append("\n".join(transcript_with_timestamps))

    except Exception as e:
        print(f"Error processing results: {str(e)}")
        raise

    # Clean up files
    try:
        # Clean up mono audio file
        os.remove(mono_path)
        print(f"\nCleaned up mono audio file: {mono_path}")
        
        # Clean up GCS
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(os.path.basename(mono_path))
        blob.delete()
        print(f"Cleaned up GCS file: {gcs_uri}")
    except Exception as e:
        print(f"Warning: Could not delete temporary files: {str(e)}")

    return transcripts

if __name__ == "__main__":
    audio_path = "/Users/wenxin/Desktop/wh/mm/data/Can The PORSCHE 911 GT3 RS Beat Its GT3 Version_I92WpL2_Ems/audio.wav"
    
    try:
        print("\n=== Starting Speech-to-Text Batch Processing with Timestamps ===")
        transcripts = transcribe_audio_with_timestamps(audio_path)
        print("\n=== Transcription Results ===")
        print("\n".join(transcripts))
    except Exception as e:
        print(f"\nError during transcription process: {str(e)}")
    finally:
        print("\n=== Processing Complete ===")


# #Google Speech to Text batch v2
# import os
# from google.cloud import storage
# from google.cloud.speech_v2 import SpeechClient
# from google.cloud.speech_v2.types import cloud_speech

# bucket_name = "cynthiastt"

# def upload_to_gcs(local_file_path, bucket_name):
#     try:
#         print(f"Uploading {os.path.basename(local_file_path)} to GCS bucket {bucket_name}...")
#         storage_client = storage.Client()
        
#         # Check if bucket exists, if not create it
#         try:
#             bucket = storage_client.get_bucket(bucket_name)
#         except Exception:
#             bucket = storage_client.create_bucket(bucket_name)
#             print(f"Created new bucket: {bucket_name}")
        
#         blob_name = os.path.basename(local_file_path)
#         blob = bucket.blob(blob_name)
#         blob.upload_from_filename(local_file_path)
#         gcs_uri = f"gs://{bucket_name}/{blob_name}"
#         print(f"Successfully uploaded to {gcs_uri}")
#         return gcs_uri
#     except Exception as e:
#         print(f"Error uploading to GCS: {str(e)}")
#         raise

# def transcribe_audio(local_file_path):
#     # Upload to GCS first
#     gcs_uri = upload_to_gcs(local_file_path, bucket_name)
    
#     # Initialize Speech client
#     client = SpeechClient()
#     project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
#     if not project_id:
#         raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")

#     # Configure recognition
#     config = cloud_speech.RecognitionConfig(
#         auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
#         language_codes=["en-US"],
#         model="long"  # Use long model for improved accuracy
#     )

#     file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=gcs_uri)

#     request = cloud_speech.BatchRecognizeRequest(
#         recognizer=f"projects/{project_id}/locations/global/recognizers/_",
#         config=config,
#         files=[file_metadata],
#         recognition_output_config=cloud_speech.RecognitionOutputConfig(
#             inline_response_config=cloud_speech.InlineOutputConfig(),
#         )
#     )

#     print("\nStarting batch transcription...")
#     operation = client.batch_recognize(request=request)
    
#     print("Waiting for operation to complete... This may take several minutes.")
#     response = operation.result(timeout=None)

#     # Process results
#     transcripts = []
#     print("\nProcessing transcription results...")
    
#     try:
#         for result in response.results[gcs_uri].transcript.results:
#             if result.alternatives:
#                 transcript = result.alternatives[0].transcript
#                 confidence = result.alternatives[0].confidence
#                 if transcript.strip():
#                     transcripts.append(f"{transcript} [confidence: {confidence:.2f}]")
#     except KeyError:
#         print(f"Warning: No results found for {gcs_uri}")
#     except Exception as e:
#         print(f"Error processing results: {str(e)}")
#         raise

#     # Optional: Clean up GCS
#     try:
#         storage_client = storage.Client()
#         bucket = storage_client.bucket(bucket_name)
#         blob = bucket.blob(os.path.basename(local_file_path))
#         blob.delete()
#         print(f"\nCleaned up GCS file: {gcs_uri}")
#     except Exception as e:
#         print(f"Warning: Could not delete GCS file: {str(e)}")

#     return transcripts

# if __name__ == "__main__":
#     audio_path = "/Users/wenxin/Desktop/wh/mm/data/Can The PORSCHE 911 GT3 RS Beat Its GT3 Version_I92WpL2_Ems/audio.wav"
    
#     try:
#         print("\n=== Starting Speech-to-Text Batch Processing ===")
#         transcripts = transcribe_audio(audio_path)
#         print("\n=== Transcription Results ===")
#         print("\n".join(transcripts))
#     except Exception as e:
#         print(f"\nError during transcription process: {str(e)}")
#     finally:
#         print("\n=== Processing Complete ===")



# #Google Speech to Text v2
# import os
# from google.cloud.speech_v2 import SpeechClient
# from google.cloud.speech_v2.types import cloud_speech
# from pydub import AudioSegment

# def split_and_transcribe(audio_path):
#     # Load and split audio into 55-second chunks
#     audio = AudioSegment.from_file(audio_path)
#     chunk_duration = 55 * 1000  # 55 seconds in milliseconds
    
#     client = SpeechClient()
#     project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

#     all_transcripts = []
#     for i in range(0, len(audio) // chunk_duration + 1):
#         start = i * chunk_duration
#         end = min((i + 1) * chunk_duration, len(audio))
#         chunk = audio[start:end]
        
#         # Export chunk
#         chunk_path = f"temp_chunk_{i}.wav"
#         chunk.export(chunk_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        
#         # Read chunk
#         with open(chunk_path, "rb") as audio_file:
#             content = audio_file.read()
        
#         # Configure recognition
#         config = cloud_speech.RecognitionConfig(
#             auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
#             language_codes=["en-US"],
#             model="long"
#         )
        
#         request = cloud_speech.RecognizeRequest(
#             recognizer=f"projects/{project_id}/locations/global/recognizers/_",
#             config=config,
#             content=content
#         )
        
#         # Get transcription
#         response = client.recognize(request=request)
        
#         # Process results
#         for result in response.results:
#             if hasattr(result, 'alternatives') and result.alternatives:
#                 timestamp = start/1000  # Convert to seconds
#                 transcript = result.alternatives[0].transcript
#                 if transcript.strip():
#                     end_time = timestamp + 5  # Approximate 5-second duration
#                     time_str = f"{int(timestamp//3600):02d}:{int((timestamp%3600)//60):02d}:{int(timestamp%60):02d},000"
#                     end_time_str = f"{int(end_time//3600):02d}:{int((end_time%3600)//60):02d}:{int(end_time%60):02d},000"
#                     all_transcripts.append(f"{time_str} --> {end_time_str}\n{transcript}\n")
        
#         # Clean up
#         os.remove(chunk_path)
    
#     return all_transcripts

# if __name__ == "__main__":
#     audio_path = "/Users/wenxin/Desktop/wh/mm/data/Can The PORSCHE 911 GT3 RS Beat Its GT3 Version_I92WpL2_Ems/audio.wav"
    
#     try:
#         print("\nTranscription Results:")
#         print("=" * 50)
#         transcripts = split_and_transcribe(audio_path)
#         print("\n".join(transcripts))
#     except Exception as e:
#         print(f"Error during transcription: {str(e)}")



#Google Speech to Text v1
# import os
# from google.cloud import speech
# from pydub import AudioSegment

# def transcribe_audio_with_timestamps(audio_path, chunk_duration=55):
#     audio = AudioSegment.from_file(audio_path)
#     chunk_duration_ms = chunk_duration * 1000
#     client = speech.SpeechClient()
    
#     for i in range(0, len(audio) // chunk_duration_ms + 1):
#         start = i * chunk_duration_ms
#         end = min((i + 1) * chunk_duration_ms, len(audio))
#         chunk = audio[start:end]
        
#         chunk_path = f"temp_chunk_{i}.wav"
#         chunk.export(chunk_path, format="wav", parameters=["-ac", "1", "-ar", "16000"])
        
#         with open(chunk_path, "rb") as audio_file:
#             content = audio_file.read()
        
#         audio_input = speech.RecognitionAudio(content=content)
#         config = speech.RecognitionConfig(
#             encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
#             sample_rate_hertz=16000,
#             language_code="en-US",
#             model="video",
#             enable_automatic_punctuation=True
#         )
        
#         try:
#             response = client.recognize(config=config, audio=audio_input)
            
#             for result in response.results:
#                 if hasattr(result, 'alternatives') and result.alternatives:
#                     timestamp = start/1000
#                     transcript = result.alternatives[0].transcript
                    
#                     if transcript.strip():
#                         hours = int(timestamp // 3600)
#                         minutes = int((timestamp % 3600) // 60)
#                         seconds = int(timestamp % 60)
#                         time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
#                         print(f"[{time_str}] {transcript}")
        
#         except Exception as e:
#             print(f"Error processing chunk {i}: {str(e)}")
        
#         finally:
#             if os.path.exists(chunk_path):
#                 os.remove(chunk_path)

# if __name__ == "__main__":
#     audio_path = "/Users/wenxin/Desktop/wh/mm/data/Can The PORSCHE 911 GT3 RS Beat Its GT3 Version_I92WpL2_Ems/audio.wav"
#     try:
#         transcribe_audio_with_timestamps(audio_path)
#     except Exception as e:
#         print(f"Error during transcription: {str(e)}")





# def extract_audio_as_wav(video_output_path, audio_output_path):
#     """Extract audio from a video file as WAV format."""
#     # Convert paths to Path objects if they are not already
#     video_output_path = Path(video_output_path)
#     audio_output_path = Path(audio_output_path)

#     if not audio_output_path.exists():
#         print(f"Extracting audio from {video_output_path}")
#         # Update the command to output WAV format
#         command = [
#             'ffmpeg', '-y', '-i', str(video_output_path),
#             '-vn',  # No video
#             '-acodec', 'pcm_s16le',  # Codec for WAV format
#             '-ar', '44100',  # Set audio sample rate (44.1 kHz)
#             '-ac', '2',  # Set number of audio channels (stereo)
#             str(audio_output_path)
#         ]
#         process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         if process.returncode != 0:
#             print(f"Failed to extract audio. Error: {process.stderr.decode()}")
#             return None
#     print(f"Audio extracted to {audio_output_path}")
#     return audio_output_path




# def generate_transcript_with_openai(audio_path):
#     """Generate a transcript using the OpenAI API and save it as an SRT file"""
#     try:
#         # Read the audio file and convert it to a base64 encoded string
#         with open(audio_path, "rb") as audio_file:
#             audio_data = audio_file.read()
        
#         # Convert the audio data to a base64 encoded string
#         encoded_string = base64.b64encode(audio_data).decode("utf-8")

#         client = OpenAI()
#         # Send the request to OpenAI
#         response = client.chat.completions.create(
#             model="gpt-4o-audio-preview",
#             modalities=["text"],
#             messages=[
#                 {
#                     "role": "user",
#                     "content": [
#                         { 
#                             "type": "text",
#                             "text": "Generate the subtitles for the deaf and hard of hearing"
#                         },
#                         {
#                             "type": "input_audio",
#                             "input_audio": {
#                                 "data": encoded_string,
#                                 "format": "wav"
#                             }
#                         }
#                     ]
#                 },
#             ]
#         )

#         transcript = response.choices[0].message.content  # Access the content property
#         print("Transcript:", transcript)
    
#     except Exception as error:
#         print("Error:", error)



