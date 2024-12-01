import os
import requests
import json

def transcribe_audio_python(audio_path):
    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    
    headers = {
        "Authorization": f"Bearer {os.getenv('GROQ_API_KEY')}"
    }
    
    try:
        with open(audio_path, 'rb') as audio_file:
            # Get the file extension from the path
            file_extension = os.path.splitext(audio_path)[1].lower()
            
            files = {
                'file': (f'audio{file_extension}', audio_file)
            }
            
            data = {
                'model': 'whisper-large-v3',
                'language': 'en',
                'response_format': 'verbose_json',
                'temperature': 0.0,
               
            }
            
            response = requests.post(url, headers=headers, files=files, data=data)
            
            if response.status_code == 200:
                result = response.json()
                print("Full Response:")
                print(json.dumps(result, indent=2))
                
                print("\nTranscribed Text:")
                print(result.get('text', 'No transcription found'))
                
                # Save to a file in the same directory as the input audio
                output_dir = os.path.dirname(audio_path)
                output_file = os.path.join(output_dir, "transcription.txt")
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result.get('text', ''))
                print(f"\nTranscription saved to {output_file}")
                
                return result
            else:
                error_message = f"Error: {response.status_code}, {response.text}"
                print(error_message)
                return error_message
                
    except FileNotFoundError:
        print(f"Could not find the file at {audio_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    # Get audio path from user input
    audio_path = input("Please enter the path to your audio file: ")
    
    # Remove quotes if the user included them
    audio_path = audio_path.strip('"\'')
    
    # Expand user directory if path starts with ~
    audio_path = os.path.expanduser(audio_path)
    
    # Convert to absolute path
    audio_path = os.path.abspath(audio_path)
    
    print(f"\nProcessing file: {audio_path}")
    transcribe_audio_python(audio_path)