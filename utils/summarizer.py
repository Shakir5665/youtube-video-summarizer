# I am making a file to hold my summarizer code so it's not all in app.py.
from google import genai
from dotenv import load_dotenv
import os
import time
import random

# We need to load our environment variables from the .env file.
load_dotenv()

# I am creating a client to talk to the Gemini API.
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    vertexai=False
)

def generate_summary(text, max_retries=3):
    # This function uses the Gemini AI to make a summary of the text.
    # It will try a few times if it fails.
    
    # First, I check if there is enough text to summarize.
    if not text or len(text.strip()) < 50:
        return """
Unable to generate summary

The video transcript is too short or empty. This usually means:
- The video has very little speech
- The video is extremely short (under 30 seconds)
- The transcript couldn't be extracted properly

Please try a different video with more spoken content.
        """.strip()
    
    # I don't want to send too much text, so I limit it to 25000 characters.
    if len(text) > 25000:
        text = text[:25000]
        print(f"Notice: Transcript trimmed to 25000 characters")
    
    # I want to try these models in order. If one fails, I try the next.
    models_to_try = ["gemini-2.5-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
    
    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                # Here I ask the model to generate the summary.
                response = client.models.generate_content(
                    model=model_name,
                    contents=f"""
                    You are a YouTube video summarizer. Analyze this transcript and provide:

                    PARAGRAPH SUMMARY
                    Write 2-3 sentences capturing the main idea of the video.

                    BULLET POINT SUMMARY
                    List 5-8 key points from the video.

                    KEY TAKEAWAYS
                    List 3 most important lessons or action items.

                    Transcript:
                    {text}
                    """
                )
                return response.text
                
            except Exception as e:
                error_msg = str(e)
                
                # If the service is unavailable, I will wait a bit and try again.
                if "503" in error_msg or "UNAVAILABLE" in error_msg:
                    if attempt < max_retries - 1:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Notice: {model_name} busy, retrying in {wait_time:.1f} seconds...")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Error: {model_name} failed, trying next model...")
                        break  # This stops the inner loop and tries the next model
                
                # If the model is not found, I move to the next one.
                elif "404" in error_msg:
                    print(f"Notice: {model_name} not found, trying next model...")
                    break
                
                # If I make too many requests, I need to tell the user to wait.
                elif "429" in error_msg or "rate limit" in error_msg.lower():
                    return """
Rate Limit Exceeded

You've reached the free tier limit. Please wait a minute and try again.

Gemini Free Tier: ~15 requests per minute, 1,500 per day
                    """.strip()
                
                # If it's a different error, I just show it.
                else:
                    return f"Error: {error_msg[:200]}"
    
    # If all models fail, I tell the user they are unavailable.
    return """
All AI models are currently unavailable

This is usually temporary. Please try:
- Waiting 1-2 minutes before retrying
- Using a different video
- Trying again during off-peak hours
    """.strip()