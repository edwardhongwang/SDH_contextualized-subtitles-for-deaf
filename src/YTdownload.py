import os
from urllib.parse import parse_qs, urlparse
import yt_dlp

def youtube_download(youtube_url):
    """Downloads YouTube video (max 720p) into its own subfolder and returns the file path."""
    try:
        # Extract video ID based on URL format
        parsed_url = urlparse(youtube_url)
        if 'youtu.be' in parsed_url.netloc:
            video_id = parsed_url.path.split('/')[1].split('?')[0]
        elif 'youtube.com' in parsed_url.netloc:
            if 'shorts' in parsed_url.path:
                video_id = parsed_url.path.split('/')[-1].split('?')[0]
            else:
                video_id = parse_qs(parsed_url.query)['v'][0]
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[ext=mp4]',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True  # Don't download playlists
        }
        
        # First get video info to get the title
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in info['title'])
            
            # Create directory structure
            video_dir = os.path.join('data', title)
            os.makedirs(video_dir, exist_ok=True)
            
            # Update options with output template
            ydl_opts.update({
                'outtmpl': os.path.join(video_dir, f"{title}.%(ext)s"),
                'extract_flat': False  # Now allow download
            })
        
        # Download the video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])
        
        return os.path.join(video_dir, f"{title}.mp4")
        
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")
    
    
if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/watch?v=hG73mW27hX4"
    print(youtube_download(youtube_url))