# 🎬 MovieMind – AI Movie Recommendation Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.11-009688.svg)](https://fastapi.tiangolo.com/)
[![Deployed on Railway](https://img.shields.io/badge/Deployed%20on-Railway-0B0D0E.svg)](https://railway.app/)

MovieMind is an intelligent, conversational AI agent that helps you discover movies through natural dialogue. Unlike traditional keyword search, MovieMind understands your taste, mood, and preferences—just like talking to a knowledgeable movie buff.

**Live Demo:** [https://moviemind-production.up.railway.app](https://moviemind-production.up.railway.app)

## ✨ Features

- 🔍 **Search movies by title** – Find any movie quickly and accurately
- 🎭 **Recommend by genre** – Action, comedy, drama, sci-fi, horror, and more
- 📊 **Get detailed info** – Cast, director, ratings, awards, overview
- ⭐ **Personalized suggestions** – Based on your taste, favorite actors, or directors
- 🧠 **Natural conversation** – No complex commands, just talk normally
- 🌐 **Web interface** – Clean, modern chat UI accessible from any device

## 🎬 Example Prompts

Here are some natural language queries you can try:

| Category | Example |
|----------|---------|
| **Genre recommendation** | "Recommend some sci-fi movies" |
| **Title search** | "Search for Inception" |
| **Movie details** | "Tell me about The Matrix" |
| **Personalized taste** | "I like Christopher Nolan films. What should I watch next?" |
| **Similar movies** | "I loved 'La La Land'. Find me something similar." |
| **Cast-based search** | "Show me Leonardo DiCaprio's best movies." |

## 🏗️ System Architecture

MovieMind is built on top of OpenManus, an open‑source general‑purpose AI agent framework. The system integrates two complementary APIs to provide comprehensive movie information:

- **TMDB API** – Primary source for movie search, genre‑based discovery, and popularity‑ranked recommendations
- **OMDb API** – Supplementary source for detailed metadata (Rotten Tomatoes scores, awards, full cast)

When you ask a question, MovieMind intelligently selects the appropriate tool (`search`, `recommend`, or `details`), fetches the data from the relevant API, and delivers a clean, conversational response—no intermediate steps or technical jargon.


## 🛠️ Tech Stack

- **Backend Framework:** FastAPI + Uvicorn
- **LLM:** OpenAI GPT‑4o‑mini (configurable)
- **APIs:** TMDB, OMDb
- **Deployment:** Railway (recommended), or any Python‑compatible platform

## 📋 Prerequisites

Before running MovieMind locally, you'll need:

- **Python 3.11+**
- **OpenAI API Key** – [Get one here](https://platform.openai.com/api-keys)
- **TMDB API Key** – [Register here](https://www.themoviedb.org/)
- **OMDb API Key** – [Request free key here](https://www.omdbapi.com/apikey.aspx)


## 📁 Project Structure
```
MovieMind/
├── web_api.py # FastAPI application entry point and frontend
├── requirements.txt # Python dependencies
├── runtime.txt # Python version specification (3.11)
├── Procfile # Production start command
├── app/
│ ├── agent/
│ │ └── manus.py # Main agent logic with custom system prompt
│ ├── tool/
│ │ └── movie_recommendation_tool.py # Custom TMDB/OMDb integration
│ ├── flow/ # Custom workflow (for extended features)
│ ├── llm.py # LLM client with environment variable override
│ └── logger.py # Logging configuration
├── config/
│ └── config.toml # LLM configuration (API keys ignored, use .env)
└── .env # Local environment variables (not committed)
```

## 🚀 Quick Start (Local)

### 1. Clone the Repository

```bash
git clone https://github.com/Xiaoda-Zhong/MovieMind.git
cd MovieMind
```

### 2. Set Up Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate        # On macOS/Linux
# .venv\Scripts\activate         # On Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a .env file in the project root:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TMDB_API_KEY=your_tmdb_api_key_here
OMDB_API_KEY=your_omdb_api_key_here
```

### 5. Run the Application
```bash
python web_api.py
```
Open your browser and navigate to: http://localhost:8000


## ☁️ Deployment (Railway)

MovieMind is ready for one‑click deployment on Railway.

1. Push your code to a GitHub repository
2. Log in to [Railway.app](https://railway.app/) and click **New Project** → **Deploy from GitHub repo**
3. Select your MovieMind repository
4. Add the following environment variables in the **Variables** tab:
   - `OPENAI_API_KEY`
   - `TMDB_API_KEY`
   - `OMDB_API_KEY`
5. Railway will automatically build and deploy your application

For other deployment platforms (Render, Vercel, etc.), refer to the platform‑specific documentation for Python/FastAPI deployment.


## Acknowledgements

- [OpenManus](https://github.com/FoundationAgents/OpenManus) – Core agent framework.
- [TMDB](https://www.themoviedb.org/) & [OMDb](http://www.omdbapi.com/) – Movie data APIs.
- [Railway](https://railway.app/) – Hosting platform.


