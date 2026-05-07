# This is the main file that runs our web application.
import gradio as gr
from utils.helpers import extract_video_id
from utils.transcript import (
    get_youtube_transcript, 
    get_transcript_with_auto_language,
    check_transcript_availability
)
from utils.summarizer import generate_summary
import os

js_code = """
function() {
    document.body.classList.add('dark');
}
"""

copy_js = """
(text) => {
    if (!text || text.includes('loading-box') || text === "Summary will appear here...") return;
    navigator.clipboard.writeText(text);
    const btn = document.querySelector('#copy-btn');
    if (btn) {
        const oldText = btn.innerText;
        btn.innerText = 'Copied!';
        setTimeout(() => { btn.innerText = oldText; }, 2000);
    }
}
"""

scroll_js = """
() => {
    // Scroll down to the right panel natively on mobile views
    if (window.innerWidth < 1024) {
        const rightPanel = document.getElementById('right-panel');
        if (rightPanel) {
            setTimeout(() => {
                rightPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 100);
        }
    }
}
"""

ultra_theme = gr.themes.Base(
    primary_hue="indigo",
    secondary_hue="purple",
    neutral_hue="slate",
    font=[gr.themes.GoogleFont("Plus Jakarta Sans"), "system-ui", "sans-serif"],
).set(
    body_background_fill="transparent",
    block_background_fill="transparent",
    block_border_width="0px",
    block_label_background_fill="transparent",
    block_label_border_width="0px",
    block_title_text_color="#94a3b8",
    panel_background_fill="transparent",
    panel_border_width="0px",
    input_background_fill="rgba(15, 23, 42, 0.6)",
    input_border_color="rgba(255, 255, 255, 0.1)",
    input_border_width="1px",
    input_border_color_focus="#8b5cf6",
    input_shadow_focus="0 0 0 3px rgba(139, 92, 246, 0.3)",
    input_radius="12px",
    input_padding="14px",
)

def summarize_video(url):
    # This function is called when we click the generate summary button.
    # First, it checks if the user entered a link.
    if not url or url.strip() == "":
        yield "Error: Please enter a YouTube URL"
        return
        
    # We show a loading message while we work.
    yield "<div class='loading-box'><span class='loader'></span><br><b style='color:#a855f7;font-size:1.1rem;font-weight:600;'>Analyzing video and generating summary...</b></div>"
    
    try:
        # We try to get the video id from the link.
        video_id = extract_video_id(url)
        if not video_id:
            yield "Error: Invalid YouTube URL\n\nPlease use:\n- https://youtube.com/watch?v=VIDEO_ID\n- https://youtu.be/VIDEO_ID"
            return
            
        print(f"Video ID: {video_id}")
        # Before downloading, we check if the video has captions.
        availability = check_transcript_availability(video_id)
        if not availability.get('has_transcripts', False):
            error = availability.get('error', 'Unknown error')
            yield f"Error: Cannot summarize this video\n\nReason: {error}\n\nTry a different video that has captions/subtitles enabled."
            return
            
        try:
            # We try to get the English captions first.
            transcript_text = get_youtube_transcript(video_id, preferred_languages=['en'])
            language_note = ""
        except Exception as e:
            try:
                # If no English, we let it find the best language automatically.
                transcript_text, language_note = get_transcript_with_auto_language(video_id)
                print(language_note)
            except Exception as e2:
                # If that fails too, we list what languages are available.
                if availability.get('languages'):
                    langs = "\n".join([f"  - {lang['name']} ({lang['code']})" for lang in availability['languages'][:5]])
                    yield f"Notice: No English transcript found\n\nAvailable languages: \n{langs}\n\nTry a video with English captions."
                else:
                    yield f"Error: Could not extract transcript: {str(e2)[:200]}"
                return
                
        # If the transcript is too short, we can't summarize it.
        if len(transcript_text) < 100:
            yield "Notice: Video too short to summarize (transcript under 100 characters)"
            return
            
        print(f"Transcript: {len(transcript_text)} chars")
        print("Generating summary...")
        # Now we ask our summarizer function to do the magic.
        summary = generate_summary(transcript_text)
        
        if language_note:
            summary = f"*{language_note}*\n\n---\n\n{summary}"
        
        yield summary
        
    except Exception as e:
        yield f"Error: {str(e)[:300]}"

def get_video_info(url):
    # This function is used to just check if a video has captions before summarizing.
    video_id = extract_video_id(url)
    if not video_id:
        return "Error: Invalid URL", ""
    
    # We create HTML to show the video thumbnail.
    thumbnail_html = f'<div class="thumbnail-box"><img src="https://img.youtube.com/vi/{video_id}/maxresdefault.jpg" onerror="this.src=\'https://img.youtube.com/vi/{video_id}/hqdefault.jpg\'" alt="Video Thumbnail"></div>'
    availability = check_transcript_availability(video_id)
    
    if availability.get('has_transcripts'):
        languages = [f"{l['name']} ({l['code']})" for l in availability.get('languages', [])]
        info_text = f"Success: Video found!\n\nAvailable transcripts: {len(availability.get('languages', []))} languages\nManual captions: {'Yes' if availability.get('has_manual') else 'No'}\nAuto-captions: {'Yes' if availability.get('has_auto') else 'No'}\nLanguages: {', '.join(languages[:5])}\n\nClick Generate Summary to continue."
        return info_text, thumbnail_html
    else:
        return f"Error: {availability.get('error', 'No transcript available')}", thumbnail_html

with open("style.css", "r", encoding="utf-8") as f:
    custom_css = f.read()

with gr.Blocks(title="YouTube Video Summarizer", theme=ultra_theme, css=custom_css, js=js_code) as app:
    with gr.Column(elem_classes="app-header"):
        gr.Markdown("<h1>AI YouTube Summarizer</h1>")
        gr.Markdown("<p>Enter a YouTube URL to get an instant AI-powered summary</p>")
    
    with gr.Row(equal_height=True):
        # Left Panel
        with gr.Column(scale=5, elem_classes="glass-panel"):
            gr.Markdown("<h3>Video Details</h3>")
            url_input = gr.Textbox(
                placeholder="https://www.youtube.com/watch?v=...",
                lines=1,
                show_label=False
            )
            
            with gr.Row():
                check_btn = gr.Button("Check Video", elem_classes="btn-secondary")
                submit_btn = gr.Button("Generate Summary", elem_classes="btn-primary")
            
            thumbnail_output = gr.HTML("")
            info_output = gr.Markdown("Enter a URL above and click Check Video", elem_classes="prose")
            
            gr.Examples(
                examples=[["https://youtu.be/mB68GanHJj4"]],
                inputs=url_input,
                label="Try this example"
            )
            
        # Right Panel
        with gr.Column(scale=7, elem_classes="glass-panel", elem_id="right-panel"):
            gr.Markdown("<h3>Generated Summary</h3>")
            output_text = gr.Markdown("Summary will appear here...", elem_classes="summary-content prose")
            copy_btn = gr.Button("Copy Summary", elem_id="copy-btn")
    
    check_btn.click(fn=get_video_info, inputs=url_input, outputs=[info_output, thumbnail_output])
    submit_btn.click(fn=None, inputs=None, outputs=None, js=scroll_js)
    submit_btn.click(fn=summarize_video, inputs=url_input, outputs=output_text)
    copy_btn.click(fn=None, inputs=[output_text], outputs=None, js=copy_js)

if __name__ == "__main__":
    print("Starting YouTube Video Summarizer...")
    print("Open http://localhost:7860")
    
    # Absolute path for favicon to guarantee it loads
    favicon_path = os.path.abspath("favicon.png")
    #app.launch(favicon_path=favicon_path)
    app.launch(
        
        server_name="0.0.0.0", 
        server_port=7860,
        favicon_path=favicon_path
    )