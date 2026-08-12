[README-2.md](https://github.com/user-attachments/files/30972943/README-2.md)
# Sage 🧠

A conversational AI chatbot with memory, built with Flask and Google's Gemini API.

## 🌐 Live Demo

[Try Sage here](https://sage-chatbot-ayxn.onrender.com)

> Note: hosted on a free instance, so the first message after a period of inactivity may take 30–50 seconds while the server wakes up.

## ✨ Features

- **Conversational memory** — Sage remembers the full context of your current chat
- **Multiple saved chats** — click "New chat" to start fresh; old conversations are saved and listed in the sidebar
- **Private per-user history** — each visitor's conversations are kept separate
- **Markdown rendering** — responses support formatted text, lists, and code blocks
- **Clean, minimal chat interface** with light typing indicators and copy-to-clipboard

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **AI:** Google Gemini API (`google-genai`)
- **Frontend:** HTML, CSS, vanilla JavaScript
- **Hosting:** Render

## 🚀 Running locally

1. Clone the repo:
   ```bash
   git clone https://github.com/sri841/sage-chatbot.git
   cd sage-chatbot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your Gemini API key as an environment variable:
   ```bash
   export GEMINI_API_KEY=your_key_here      # macOS/Linux
   set GEMINI_API_KEY=your_key_here         # Windows
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## 📦 Deployment

This app is deployed on [Render](https://render.com) as a Python web service.

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn app:app --timeout 120`
- **Environment variables required:**
  - `GEMINI_API_KEY` — your Google Gemini API key
  - `SECRET_KEY` — any random string, used to sign user session cookies

## 📁 Project Structure

```
sage-chatbot/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html         # Frontend UI
└── README.md
```
