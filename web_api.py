# web_api.py
import sys
from dotenv import load_dotenv
load_dotenv()   # 加载项目根目录下的 .env 文件
from pathlib import Path

# Add project root to Python path for proper imports
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from app.agent.manus import Manus
from app.logger import logger
import logging
import re

# Suppress verbose logs from OpenManus internal modules
logging.getLogger("app.agent").setLevel(logging.WARNING)
logging.getLogger("app.llm").setLevel(logging.WARNING)
logging.getLogger("app.tool").setLevel(logging.WARNING)
logging.getLogger("app.flow").setLevel(logging.WARNING)

# ---------- Helper: Clean agent output ----------
def clean_agent_output(text: str) -> str:
    """
    Remove step prefixes (e.g., "Step 1:") but keep the rest of the line.
    Remove lines that start with "Observed output of cmd" entirely.
    Also remove other intermediate artifacts like termination messages.
    """
    if not text:
        return text

    lines = text.split('\n')
    cleaned_lines = []
    step_pattern = re.compile(r'^Step\s+\d+:\s*', re.IGNORECASE)

    for line in lines:
        line_without_step = step_pattern.sub('', line)

        if re.match(r'^Observed output of cmd', line_without_step.strip(), re.IGNORECASE):
            continue
        if re.match(r'^The interaction has been completed', line_without_step.strip(), re.IGNORECASE):
            continue

        trimmed = line_without_step.strip()
        if trimmed:
            cleaned_lines.append(line_without_step)

    result = '\n'.join(cleaned_lines).strip()
    return result if result else text

# ---------- Data Models ----------
class TaskRequest(BaseModel):
    prompt: str

class TaskResponse(BaseModel):
    success: bool
    result: str

# ---------- FastAPI Application ----------
app = FastAPI(title="MovieMind API", description="MovieMind - AI Movie Recommendation Agent")

# Global Agent instance
agent = Manus()

# ---------- Task Execution API ----------
@app.post("/run", response_model=TaskResponse)
async def run_agent(request: TaskRequest):
    try:
        logger.info(f"📥 Received task: {request.prompt}")
        result = await agent.run(request.prompt)
        cleaned_result = clean_agent_output(result)
        return TaskResponse(success=True, result=cleaned_result)
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Health Check ----------
@app.get("/health")
async def health():
    return {"status": "alive"}

# ---------- Main Page (MovieMind Style) ----------
@app.get("/", response_class=HTMLResponse)
async def serve_moviemind_ui():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>MovieMind · AI Movie Recommender</title>
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🎬</text></svg>">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', system-ui, sans-serif;
            background: linear-gradient(135deg, #f5f7fc 0%, #eef2f8 100%);
            height: 100vh;
            overflow: hidden;
        }

        .app {
            display: flex;
            height: 100vh;
            width: 100%;
        }

        /* Left sidebar - MovieMind info */
        .sidebar {
            width: 300px;
            background: rgba(255,255,255,0.85);
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(0,0,0,0.05);
            display: flex;
            flex-direction: column;
            padding: 1.5rem;
            box-shadow: 2px 0 12px rgba(0,0,0,0.02);
        }

        .logo {
            font-size: 1.8rem;
            font-weight: 600;
            background: linear-gradient(135deg, #1e2b3c, #2c3e50);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .logo span {
            font-size: 2rem;
        }

        .info-section {
            margin-bottom: 1.5rem;
        }

        .info-title {
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #6c7a8a;
            margin-bottom: 0.75rem;
        }

        .info-text {
            font-size: 0.85rem;
            color: #2c3e50;
            line-height: 1.5;
        }

        .feature-list {
            list-style: none;
            margin-top: 0.5rem;
        }
        .feature-list li {
            font-size: 0.8rem;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .badge {
            background: #eef2ff;
            border-radius: 1rem;
            padding: 0.2rem 0.6rem;
            font-size: 0.7rem;
            color: #1e293b;
        }

        /* Right chat area */
        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 2rem 2rem 1rem 2rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
        }

        .message {
            display: flex;
            gap: 1rem;
            max-width: 85%;
            animation: fadeInUp 0.25s ease-out;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: #eef2ff;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2rem;
            flex-shrink: 0;
        }

        .message.user .avatar {
            background: #1e293b;
            color: white;
        }

        .bubble {
            background: white;
            padding: 0.85rem 1.2rem;
            border-radius: 1.5rem;
            border-top-left-radius: 0.25rem;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
            line-height: 1.5;
            font-size: 0.95rem;
            color: #1e293b;
            word-break: break-word;
            white-space: pre-wrap;
        }

        .message.user .bubble {
            background: #1e293b;
            color: white;
            border-top-right-radius: 0.25rem;
            border-top-left-radius: 1.5rem;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            align-items: center;
            padding: 0.5rem 1rem;
        }
        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #94a3b8;
            border-radius: 50%;
            animation: pulse 1.2s infinite ease-in-out;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse {
            0%, 60%, 100% { transform: scale(0.8); opacity: 0.5; }
            30% { transform: scale(1.2); opacity: 1; }
        }

        .input-area {
            background: white;
            border-top: 1px solid #e9edf2;
            padding: 1rem 2rem 1.5rem 2rem;
        }

        .input-container {
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            gap: 0.75rem;
            align-items: flex-end;
            background: #f8fafc;
            border-radius: 2rem;
            padding: 0.5rem 0.5rem 0.5rem 1.2rem;
            border: 1px solid #e2e8f0;
            transition: all 0.2s;
        }

        .input-container:focus-within {
            border-color: #94a3b8;
            box-shadow: 0 0 0 2px rgba(100,108,255,0.2);
        }

        textarea {
            flex: 1;
            border: none;
            background: transparent;
            font-family: inherit;
            font-size: 0.95rem;
            padding: 0.75rem 0;
            resize: none;
            outline: none;
            max-height: 200px;
        }

        button {
            background: #1e293b;
            border: none;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 1.2rem;
        }

        button:hover {
            background: #0f172a;
            transform: scale(0.96);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .footer-note {
            text-align: center;
            font-size: 0.7rem;
            color: #7e8b9c;
            margin-top: 0.75rem;
        }

        ::-webkit-scrollbar {
            width: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 4px;
        }

        @media (max-width: 680px) {
            .sidebar {
                display: none;
            }
            .message {
                max-width: 95%;
            }
            .messages {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
<div class="app">
    <aside class="sidebar">
        <div class="logo">
            <span>🎬</span> MovieMind
        </div>
        <div class="info-section">
            <div class="info-title">🎯 Your Personal Movie AI</div>
            <div class="info-text">
                Just tell me what you're in the mood for — genre, actor, or simply "something interesting" — and I'll recommend the perfect films.
            </div>
        </div>
        <div class="info-section">
            <div class="info-title">✨ What I can do</div>
            <ul class="feature-list">
                <li>🔍 Search movies by title</li>
                <li>🎭 Recommend by genre (action, comedy, drama, sci-fi, etc.)</li>
                <li>📊 Get detailed info (cast, ratings, awards)</li>
                <li>⭐ Personalized suggestions based on your taste</li>
            </ul>
        </div>
        <div class="info-section">
            <div class="info-title">💬 Example prompts</div>
            <div class="badge" style="display: inline-block; margin: 0.25rem;">"Recommend action movies"</div>
            <div class="badge" style="display: inline-block; margin: 0.25rem;">"Search for Inception"</div>
            <div class="badge" style="display: inline-block; margin: 0.25rem;">"Tell me about The Matrix"</div>
        </div>
        <div style="margin-top: auto; font-size: 0.7rem; color: #8b9ab0; padding-top: 1rem; border-top: 1px solid #e2e8f0;">
            Powered by TMDB & OMDb
        </div>
    </aside>

    <div class="chat-area">
        <div class="messages" id="messages">
            <div class="message assistant">
                <div class="avatar">🎬</div>
                <div class="bubble">
                    🍿 Hi, I'm <strong>MovieMind</strong>!<br><br>
                    Tell me what you'd like to watch — by genre, mood, or title.<br>
                    Try: <em>"Recommend sci‑fi movies"</em> or <em>"Give me details about Interstellar"</em>.
                </div>
            </div>
        </div>
        <div class="input-area">
            <div class="input-container">
                <textarea id="promptInput" rows="1" placeholder="Ask for movie recommendations... (Enter to send)"></textarea>
                <button id="sendBtn" aria-label="Send">➤</button>
            </div>
            <div class="footer-note">MovieMind · AI movie recommender</div>
        </div>
    </div>
</div>

<script>
    const messagesDiv = document.getElementById('messages');
    const promptInput = document.getElementById('promptInput');
    const sendBtn = document.getElementById('sendBtn');
    let isLoading = false;

    promptInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });

    async function sendMessage() {
        if (isLoading) return;
        const text = promptInput.value.trim();
        if (!text) return;

        promptInput.value = '';
        promptInput.style.height = 'auto';

        addMessage(text, 'user');
        const loadingId = addTypingIndicator();
        isLoading = true;
        sendBtn.disabled = true;

        try {
            const response = await fetch('/run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });
            const data = await response.json();
            removeTypingIndicator(loadingId);
            if (data.success) {
                addMessage(data.result, 'assistant');
            } else {
                addMessage('❌ Error: ' + (data.detail || 'Unknown error'), 'assistant');
            }
        } catch (err) {
            removeTypingIndicator(loadingId);
            addMessage('❌ Network error: ' + err.message, 'assistant');
        } finally {
            isLoading = false;
            sendBtn.disabled = false;
            promptInput.focus();
        }
    }

    function addMessage(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        const avatar = role === 'user' ? '👤' : '🎬';
        messageDiv.innerHTML = `
            <div class="avatar">${avatar}</div>
            <div class="bubble">${escapeHtml(content).replace(/\\n/g, '<br>')}</div>
        `;
        messagesDiv.appendChild(messageDiv);
        scrollToBottom();
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'message assistant';
        div.innerHTML = `
            <div class="avatar">🎬</div>
            <div class="bubble">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesDiv.appendChild(div);
        scrollToBottom();
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function scrollToBottom() {
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }

    function escapeHtml(str) {
        return str.replace(/[&<>]/g, function(m) {
            if (m === '&') return '&amp;';
            if (m === '<') return '&lt;';
            if (m === '>') return '&gt;';
            return m;
        });
    }

    sendBtn.addEventListener('click', sendMessage);
    promptInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    promptInput.focus();
</script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
