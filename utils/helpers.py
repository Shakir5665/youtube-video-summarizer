# utils/helpers.py
import re

def extract_video_id(url):
    """
    Extract YouTube video ID from various URL formats
    
    Examples:
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ
    - https://youtu.be/dQw4w9WgXcQ
    - https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120s
    """
    # Pattern for youtu.be format
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[1].split("?")[0]
        if len(video_id) == 11:  # YouTube IDs are 11 characters
            return video_id
    
    # Pattern for youtube.com format with v= parameter
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    
    # Pattern for embedded videos
    match = re.search(r"embed/([a-zA-Z0-9_-]{11})", url)
    if match:
        return match.group(1)
    
    return None