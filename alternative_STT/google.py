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
