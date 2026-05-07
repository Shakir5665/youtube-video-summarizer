# I'm writing this file to keep my helper functions in one place.
# We need the re module because we will use regular expressions to find things in strings.
import re

def extract_video_id(url):
    # This function takes a link and tries to find the video id.
    # A video link could look like this:
    # https://www.youtube.com/watch?v=dQw4w9WgXcQ
    # or this: https://youtu.be/dQw4w9WgXcQ
    
    # First, let's check if the link is a short youtu.be link.
    if "youtu.be/" in url:
        # I split the link by youtu.be/ and take the second part.
        # Then I split again by ? to remove extra stuff at the end.
        video_id = url.split("youtu.be/")[1].split("?")[0]
        # I learned that YouTube ids always have exactly 11 characters.
        if len(video_id) == 11:
            return video_id
    
    # If it's a normal youtube.com link, I will use regular expressions to find the v= part.
    # The id is always 11 letters, numbers, dashes or underscores.
    match = re.search(r"v=([a-zA-Z0-9_-]{11})", url)
    if match:
        # I return the first group from the match.
        return match.group(1)
    
    # Sometimes videos are embedded in other sites. We need to check for embed/ in the link.
    match = re.search(r"embed/([a-zA-Z0-9_-]{11})", url)
    if match:
        # Returning the match if we find one.
        return match.group(1)
    
    # If none of the above worked, we just return None to say we didn't find anything.
    return None