# 📺 YouTube Chatbot Extension

This project is a **YouTube-integrated chatbot** powered by Python and JavaScript. It combines a **Chrome Extension frontend** with a **Python AI backend** to provide smart, context-aware interaction with YouTube content.

---

## 🚀 Features

- 🧠 Chatbot that understands and summarizes YouTube videos
- 🌐 Chrome Extension interface with `popup.html`
- 🔁 Backend powered by `app.py` and `pipeline.py`
- 📡 Communicates between frontend (JavaScript) and backend (Python API)
- 📦 Lightweight and modular design

---

## 🗂️ Project Structure
Youtube-Chatbot-Extension/
│
├── youtube-ai-extension/ # Chrome extension source
│ ├── manifest.json # Extension config
│ ├── popup.html # Chatbot UI
│ └── popup.js # JavaScript logic
│
├── app.py # Flask (or FastAPI) server backend
├── pipeline.py # NLP/AI processing pipeline
├── requirements.txt # Python dependencies
├── .env # Environment variables
├── .gitignore # Git ignore rules
└── README.md # Project overview


## Install Requirements
pip install -r requirements.txt

## Set Environment Variables
OPENAI_API_KEY=your_key_here

## Run Backend
python app.py

## Chrome Extension Setup
1. Load the Extension
2. Open Chrome → chrome://extensions/
3. Enable Developer Mode
4. Click "Load unpacked"
5. Select the youtube-ai-extension/ folder

🙋‍♀️ Maintainer
Sneha Gupta
AI Developer @ Meril Life Sciences
GitHub: @Snehagupta13




