# utils/transcript.py - Fixed with actual error classes
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
    InvalidVideoId,
    NotTranslatable,
    TranslationLanguageNotAvailable
)

# Note: TooManyRequests doesn't exist in this version
# We'll handle rate limits differently

def get_youtube_transcript(video_id, preferred_languages=['en']):
    """
    Fetch transcript from YouTube video with intelligent fallback
    
    Args:
        video_id: YouTube video ID (11 characters)
        preferred_languages: List of language codes to try (default: ['en'])
    
    Returns:
        String containing the full transcript with language note
    
    Raises:
        Exception with user-friendly error message
    """
    
    ytt_api = YouTubeTranscriptApi()
    
    # Step 1: Try to get transcript in preferred languages
    for language in preferred_languages:
        try:
            transcript_data = ytt_api.fetch(video_id, languages=[language])
            transcript_text = " ".join([item.text for item in transcript_data])
            return transcript_text
            
        except NoTranscriptFound:
            continue  # Try next language
        except TranscriptsDisabled:
            raise Exception("⚠️ Captions are disabled for this video. Creator has turned off subtitles.")
        except VideoUnavailable:
            raise Exception("❌ Video is unavailable. It may be private or deleted.")
        except InvalidVideoId:
            raise Exception("❌ Invalid YouTube video ID. Please check the URL.")
        except Exception as e:
            # Check if it's a rate limit error by looking at the message
            error_msg = str(e)
            if "429" in error_msg or "too many" in error_msg.lower():
                raise Exception("⏰ Too many requests. Please try again in a few minutes.")
            continue  # Try next language for other errors
    
    # Step 2: If no transcript in preferred languages, list all available transcripts
    try:
        transcript_list = ytt_api.list(video_id)
        
        available_languages = []
        for transcript in transcript_list:
            lang_code = transcript.language_code
            lang_name = transcript.language
            is_generated = "auto-generated" if transcript.is_generated else "manual"
            available_languages.append(f"  • {lang_name} ({lang_code}) - {is_generated}")
        
        if available_languages:
            languages_list = "\n".join(available_languages)
            raise Exception(f"""
📝 **No transcript in your preferred languages.**

**Available transcripts for this video:**
{languages_list}

💡 **Try using a different video or add language codes to the function.**
            """.strip())
        else:
            raise Exception("📝 No transcript available for this video. The video may have no captions at all.")
            
    except NoTranscriptFound:
        raise Exception("📝 No transcript available for this video. The video may have no captions.")
    except TranscriptsDisabled:
        raise Exception("⚠️ Captions are disabled for this video.")
    except Exception as e:
        raise Exception(f"❌ Failed to fetch transcript: {str(e)}")


def get_transcript_with_auto_language(video_id):
    """
    Automatically detect and fetch the best available transcript
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Tuple of (transcript_text, detected_language)
    """
    
    ytt_api = YouTubeTranscriptApi()
    
    try:
        # Get list of all available transcripts
        transcript_list = ytt_api.list(video_id)
        
        # Priority order: manual En → auto En → any manual → any auto
        best_transcript = None
        priority_score = -1
        
        for transcript in transcript_list:
            score = 0
            # Manual transcripts are better than auto-generated
            if not transcript.is_generated:
                score += 10
            # English is preferred
            if transcript.language_code == 'en':
                score += 5
            # Shorter language codes are usually primary languages
            score += (10 - len(transcript.language_code))
            
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
    """
    Check what transcripts are available without fetching them
    
    Args:
        video_id: YouTube video ID
    
    Returns:
        Dictionary with availability information
    """
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
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