# 🎥 AI YouTube Video Summarizer

A sleek, AI-powered web application that generates instant summaries, key takeaways, and bullet points from any YouTube video. This project is a **first-step learning project**, built to understand the integration of Gradio, Google Gemini AI, and YouTube transcripts. Features and functionality will be continuously enhanced in the future!

🌐 **Live Demo:** [https://youtube-video-summarizer-7vmt.onrender.com](https://youtube-video-summarizer-7vmt.onrender.com)

> **⚠️ Note on Live Deployment:** The live deployment hosted on Render is currently facing an issue where YouTube blocks the cloud IP from fetching transcripts. This is a known issue (not yet fixed) for cloud deployments. However, **the application works perfectly when run locally!**

---

## 🚀 Features
- **Instant Video Summarization:** Get paragraph summaries, bullet points, and key takeaways using Google Gemini AI.
- **Smart Transcript Fetching:** Automatically fetches English transcripts or falls back to auto-generated/available languages.
- **Responsive UI:** A beautiful glassmorphism-themed interface built with Gradio and custom CSS.
- **Copy to Clipboard:** Easily copy the generated summary with one click.

---

## 📁 Folder Structure

```text
youtube-video-summarizer/
│
├── app.py                 # Main entry point and Gradio UI setup
├── style.css              # Custom styles for the user interface
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (API Keys)
├── favicon.png            # Website Favicon
└── utils/                 # Helper modules
    ├── __init__.py
    ├── helpers.py         # URL extraction and utilities
    ├── summarizer.py      # Google Gemini API integration
    └── transcript.py      # YouTube transcript fetching logic
```

---

## 💻 How to Run Locally

Since YouTube may block cloud IPs, the best way to use this summarizer is by running it on your local machine.

### 1. Prerequisites
- Python 3.8+ installed on your system.
- A free [Google Gemini API Key](https://aistudio.google.com/app/apikey).

### 2. Installation Steps

**Clone the repository (or download the files):**
```bash
git clone https://github.com/yourusername/youtube-video-summarizer.git
cd youtube-video-summarizer
```

**Create a virtual environment (Recommended):**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**Install the dependencies:**
```bash
pip install -r requirements.txt
```

**Set up your Environment Variables:**
Create a `.env` file in the root directory and add your Gemini API Key:
```env
GEMINI_API_KEY=your_google_gemini_api_key_here
```

**Run the Application:**
```bash
python app.py
```
Open your browser and navigate to `http://localhost:7860`.

---

## Problems Solved Along the Way

Throughout the development of this learning project, several hurdles were overcome:

**1. Import & Installation Issues**
- **Challenge:** Package not found
  **Resolution:** Installed correctly inside the virtual environment.
- **Challenge:** Wrong SDK version
  **Resolution:** Switched to the updated `google-genai` SDK.

**2. API & Authentication**
- **Challenge:** API key not working
  **Resolution:** Created a new valid key in Google AI Studio.
- **Challenge:** VertexAI routing issues
  **Resolution:** Set `vertexai=False` in the client configuration.

**3. Model Errors**
- **Challenge:** `gemini-1.0-pro` not found
  **Resolution:** Upgraded to use `gemini-2.5-flash` and `gemini-1.5-flash`.
- **Challenge:** Model name format errors
  **Resolution:** Corrected model name syntax per the latest API documentation.

**4. Server Errors**
- **Challenge:** 503 Service Unavailable
  **Resolution:** Added exponential backoff and retry logic in the summarizer to handle rate limits and busy servers gracefully.

**5. Gradio Compatibility**
- **Challenge:** `allow_flagging` parameter error
  **Resolution:** Updated code parameters to be compatible with Gradio 6.x.

**6. YouTube Transcript Issues**
- **Challenge:** No transcript available
  **Resolution:** Built a robust fallback system to detect and pull transcripts in any available language (auto-generated or manual).
- **Challenge:** Wrong attribute names
  **Resolution:** Fixed dictionary parsing (`item.text` vs `item['text']`).

---

## 🔮 Future Enhancements
As this is a foundational learning project, future updates will include:
- Fixing the cloud IP block issue for live deployments.
- Support for translating summaries into multiple languages.
- Adding timestamped chapter breakdowns.
- Allowing users to chat with the video transcript.

---

*Built with ❤️ using Python, Gradio, and Google Gemini AI.*
