# I made this file to handle getting the text from YouTube videos.
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    InvalidVideoId,
    NotTranslatable,
    TranslationLanguageNotAvailable
)

def get_youtube_transcript(video_id, preferred_languages=['en']):
    # This function tries to get the transcript in a language we prefer.
    # It takes the video id and a list of languages.
    
    ytt_api = YouTubeTranscriptApi()
    
    # First, we try to get the transcript in our preferred languages.
    for language in preferred_languages:
        try:
            transcript_data = ytt_api.fetch(video_id, languages=[language])
            transcript_text = " ".join([item.text for item in transcript_data])
            return transcript_text
            
        except NoTranscriptFound:
            continue  # If we don't find it, we just try the next language.
        except TranscriptsDisabled:
            raise Exception("Notice: Captions are disabled for this video. Creator has turned off subtitles.")
        except VideoUnavailable:
            raise Exception("Error: Video is unavailable. It may be private or deleted.")
        except InvalidVideoId:
            raise Exception("Error: Invalid YouTube video ID. Please check the URL.")
        except Exception as e:
            # We check if we asked YouTube too many times and they told us to wait.
            error_msg = str(e)
            if "429" in error_msg or "too many" in error_msg.lower():
                raise Exception("Notice: Too many requests. Please try again in a few minutes.")
            continue  # Try next language for other errors
    
    # If we couldn't find our preferred languages, we list all available ones.
    try:
        transcript_list = ytt_api.list(video_id)
        
        available_languages = []
        for transcript in transcript_list:
            lang_code = transcript.language_code
            lang_name = transcript.language
            is_generated = "auto-generated" if transcript.is_generated else "manual"
            available_languages.append(f"  - {lang_name} ({lang_code}) - {is_generated}")
        
        if available_languages:
            languages_list = "\n".join(available_languages)
            raise Exception(f"""
Notice: No transcript in your preferred languages.

Available transcripts for this video:
{languages_list}

Try using a different video or add language codes to the function.
            """.strip())
        else:
            raise Exception("Notice: No transcript available for this video. The video may have no captions at all.")
            
    except NoTranscriptFound:
        raise Exception("Notice: No transcript available for this video. The video may have no captions.")
    except TranscriptsDisabled:
        raise Exception("Notice: Captions are disabled for this video.")
    except Exception as e:
        raise Exception(f"Error: Failed to fetch transcript: {str(e)}")


def get_transcript_with_auto_language(video_id):
    # This function automatically picks the best transcript it can find.
    
    ytt_api = YouTubeTranscriptApi()
    
    try:
        # We get the list of all available transcripts
        transcript_list = ytt_api.list(video_id)
        
        # We will keep track of the best one we find using a score.
        best_transcript = None
        priority_score = -1
        
        for transcript in transcript_list:
            score = 0
            # We prefer human-written transcripts over auto-generated ones.
            if not transcript.is_generated:
                score += 10
            # We prefer English if possible.
            if transcript.language_code == 'en':
                score += 5
            # Short language codes usually mean it's a main language.
            score += (10 - len(transcript.language_code))
            
            # If this transcript has a better score, it becomes the new best.
            if score > priority_score:
                priority_score = score
                best_transcript = transcript
        
        if best_transcript:
            transcript_data = best_transcript.fetch()
            transcript_text = " ".join([item.text for item in transcript_data])
            
            language_info = f"[Using {best_transcript.language} ({best_transcript.language_code}) - {'manual' if not best_transcript.is_generated else 'auto-generated'} transcript]"
            
            return transcript_text, language_info
        else:
            raise Exception("No transcripts found")
            
    except Exception as e:
        raise Exception(f"Could not fetch any transcript: {str(e)}")


def check_transcript_availability(video_id):
    # This function just checks what transcripts exist without downloading them.
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # We create a dictionary to store what we found.
        available = {
            'has_transcripts': True,
            'languages': [],
            'has_manual': False,
            'has_auto': False,
            'has_english': False
        }
        
        for transcript in transcript_list:
            lang_info = {
                'code': transcript.language_code,
                'name': transcript.language,
                'is_generated': transcript.is_generated,
                'is_manual': not transcript.is_generated
            }
            available['languages'].append(lang_info)
            
            if not transcript.is_generated:
                available['has_manual'] = True
            else:
                available['has_auto'] = True
                
            if transcript.language_code == 'en':
                available['has_english'] = True
        
        return available
        
    except NoTranscriptFound:
        return {'has_transcripts': False, 'error': 'No transcripts available for this video'}
    except TranscriptsDisabled:
        return {'has_transcripts': False, 'error': 'Captions are disabled by the video creator'}
    except Exception as e:
        return {'has_transcripts': False, 'error': str(e)}