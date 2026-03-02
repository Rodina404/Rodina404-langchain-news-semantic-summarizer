# 📰 LangChain News Semantic Summarizer

> AI-powered news summarization with semantic search — built with **LangChain**, **Groq**, **Google Gemini**, and **ChromaDB**.

![Python](https://img.shields.io/badge/Python-3.10+-purple?style=for-the-badge&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-Framework-blueviolet?style=for-the-badge)
![Flask](https://img.shields.io/badge/Flask-Web_UI-mediumpurple?style=for-the-badge&logo=flask&logoColor=white)

---
<img width="1918" height="911" alt="Screenshot 2026-03-02 232203" src="https://github.com/user-attachments/assets/a8fb0340-752f-4167-9f91-573e9c90937c" />


## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **News Retrieval** | Fetches real-time articles from [NewsAPI](https://newsapi.org/) on any topic |
| 🧠 **Semantic Embeddings** | Vectorises articles using Google Gemini (`gemini-embedding-001`) |
| 📦 **Vector Storage** | Stores embeddings in ChromaDB for fast similarity search |
| 📝 **Two Summary Modes** | **Brief** (1-2 sentences, stuff chain) and **Detailed** (paragraph, map_reduce chain) |
| 💾 **User Preferences** | Saves favourite topics, default mode, and full search history in JSON |
| 💻 **CLI Interface** | Colourful interactive terminal menu |
| 🌸 **Web UI** | Beautiful purple/lilac/lavender themed Flask web app with glassmorphism |

---

## 🏗️ Project Structure

```
langchain-news-semantic-summarizer/
│
├── news_retriever.py      # NewsAPI integration — fetch articles as Documents
├── embedding_engine.py    # Gemini embeddings + Chroma vector store + search
├── summarizer.py          # LangChain summarization chains (stuff / map_reduce)
├── user_manager.py        # JSON-based user preferences & history
├── main.py                # CLI entry point (interactive menu)
├── app.py                 # Flask web application
│
├── templates/
│   └── index.html         # Web UI template (purple themed)
├── static/
│   ├── style.css          # CSS design system (lilac/lavender glassmorphism)
│   └── app.js             # Frontend JavaScript logic
│
├── requirements.txt       # Python dependencies
├── .env.example           # API key template
├── Summarization_Task.ipynb  # Original Colab notebook
└── README.md              # This file
```

---

## 🔧 Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/Rodina404/langchain-news-semantic-summarizer.git
cd langchain-news-semantic-summarizer
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up API keys

Copy the example env file and fill in your keys:

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
NEWSAPI_KEY=your_newsapi_key_here          # https://newsapi.org/register
GROQ_API_KEY=your_groq_api_key_here        # https://console.groq.com/keys
GOOGLE_API_KEY=your_google_api_key_here    # https://aistudio.google.com/app/apikey
```

---

## 🚀 Usage

### Option A: Web UI (Recommended)

```bash
python app.py
```

Open **http://localhost:5000** in your browser. You'll see the purple-themed interface where you can:

- 🔍 Search any news topic
- 🎯 Choose brief or detailed summary mode
- 💜 Save favourite topics in the sidebar
- 🕑 Review your search history
- ⚙️ Set your default preference

### Option B: Command-Line Interface

```bash
python main.py
```

Interactive menu:
```
╔══════════════════════════════════════════╗
║   📰  News Semantic Summarizer  📰      ║
╚══════════════════════════════════════════╝
  1) Search news by topic
  2) Save a topic
  3) View saved topics
  4) Set default summary mode (brief / detailed)
  5) View search history
  q) Quit
```

---

## 🔌 API Endpoints (Web UI)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/search?topic=X&mode=brief&query=Y` | Search, embed & summarize |
| `GET` | `/api/topics` | List saved topics |
| `POST` | `/api/topics` | Save a topic (`{"topic": "..."}`) |
| `DELETE` | `/api/topics` | Remove a topic (`{"topic": "..."}`) |
| `GET` | `/api/history` | Get search history |
| `GET` | `/api/preferences` | Get preferences |
| `POST` | `/api/preferences` | Set default mode (`{"default_mode": "brief"}`) |

---

## 🧩 How It Works

<img width="815" height="290" alt="image" src="https://github.com/user-attachments/assets/cba9f094-7983-4d78-a51f-7c32908050c2" />


1. **Fetch** — `news_retriever.py` pulls articles from NewsAPI's "everything" endpoint
2. **Embed** — `embedding_engine.py` splits text into chunks & vectorises with Gemini
3. **Search** — Semantic similarity search finds the most relevant chunks
4. **Summarize** — `summarizer.py` runs a LangChain chain:
   - `"brief"` → **stuff** chain (fast, single-pass, 1-2 sentences)
   - `"detailed"` → **map_reduce** chain (processes each chunk, then merges)
5. **Store** — `user_manager.py` persists topics, preferences, and history to `user_data.json`

---

## 📦 Dependencies

- `langchain`, `langchain-core`, `langchain-classic`
- `langchain-google-genai` — Google Gemini embeddings
- `langchain-groq` — Groq LLM (LLaMA 3.1 8B Instant)
- `langchain-chroma`, `chromadb` — Vector storage
- `langchain-text-splitters` — Document chunking
- `flask` — Web framework
- `requests` — HTTP client
- `python-dotenv` — Environment variable management

---

## 📄 License

This project is for educational purposes as part of an AI-based course assignment.

---

<p align="center">
  Made with 💜 using LangChain & AI
</p>
