# MemoryLane AI

An AI that remembers your relationship better than you do.

Feed it your WhatsApp chat history — it uses RAG + GPT-5.1 to chat about your memories, roast you with real stats, generate quizzes, build a relationship timeline, and write stories about you.

![MemoryLane Banner](https://placehold.co/1200x400/070711/8b5cf6?text=MemoryLane+AI&font=montserrat)

---

## Features

| Mode | What it does |
|------|-------------|
| 💬 **Chat** | Ask anything about your relationship — RAG retrieves the exact memories |
| 🔥 **Roast** | Gets roasted based on real stats (who texts more, response time, catchphrases) |
| 🧠 **Quiz** | Auto-generated trivia questions from your actual chat history |
| 💫 **Timeline** | Identifies phases in your relationship, outputs a narrative |
| ✍️ **Story** | Writes a story/poem/Bollywood script about you two |
| 📊 **Analytics** | Message counts, emoji frequency, response times, monthly activity |

---

## Tech Stack

```
Frontend    Next.js 14 (App Router) · Tailwind CSS · Vercel
Backend     FastAPI · Python 3.12 · Render
LLM         OpenAI GPT-5.1
Embeddings  text-embedding-3-small
Vector DB   Chroma (local, baked into deployment)
```

---

## How it works

```
WhatsApp .txt export
        ↓
   Parse + clean          (85k+ messages, removes media/system msgs, keeps emojis)
        ↓
   Chunk (7 msgs)         (12,202 chunks preserving conversational context)
        ↓
   Embed + store          (text-embedding-3-small → Chroma DB)
        ↓
   User query → RAG       (top-5 similar chunks retrieved)
        ↓
   GPT-5.1 + personality  (playful, emotionally aware, Hinglish-friendly)
        ↓
   Streamed response
```

---

## Local Setup

**Prerequisites:** Python 3.11+, Node.js 18+, OpenAI API key

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install fastapi "uvicorn[standard]" pydantic-settings "openai>=1.55" "chromadb>=0.5" python-multipart

# Add your API key
cp .env.example .env
# Edit .env → set OPENAI_API_KEY=sk-...

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install

# Point at local backend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
# → http://localhost:3000
```

### Load your chat data

1. Export WhatsApp chat: **Open chat → ⋮ → More → Export Chat → Without Media**
2. Open `http://localhost:3000` → click **Upload Chat**
3. Drop the `.txt` file — embeddings generate in ~3 minutes

---

## Deployment

**Frontend → Vercel** (free)
- Root directory: `frontend`
- Env var: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`

**Backend → Render** (free)
- Runtime: Docker
- `render.yaml` is included — Render auto-detects it
- Env var: `OPENAI_API_KEY=sk-...`

The Chroma embeddings are baked into the repo — no upload step needed at runtime.

---

## Project Structure

```
memorylane-ai/
├── backend/
│   ├── main.py              # FastAPI app + all routes
│   ├── config.py            # Settings (pydantic-settings)
│   ├── data_processor.py    # WhatsApp parser + chunker
│   ├── embeddings.py        # Chroma vector store
│   ├── rag.py               # Context builder + personality prompt
│   ├── analytics.py         # Stats engine
│   ├── llm.py               # OpenAI wrapper (streaming)
│   ├── features/
│   │   ├── chat.py          # Streaming RAG chat
│   │   ├── roast.py         # Roast generator
│   │   ├── quiz.py          # Quiz generator
│   │   ├── timeline.py      # Timeline generator
│   │   └── story.py         # Story/poem generator
│   ├── data/                # Baked Chroma DB + analytics
│   └── Dockerfile
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/
│   │   ├── modes/           # One component per feature
│   │   └── ui/              # GlassCard, LoadingDots, etc.
│   └── lib/api.ts           # Typed API client
└── render.yaml              # Render deployment config
```

---

## API Endpoints

```
POST   /upload       Upload WhatsApp .txt → parse + embed
POST   /chat         Streaming RAG chat (SSE)
GET    /roast        Roast based on chat stats
GET    /quiz         Generate relationship trivia
GET    /timeline     Relationship phases narrative
GET    /story        Story/poem in chosen style
GET    /analytics    Full stats JSON
DELETE /data         Wipe all stored data
```

---

## Privacy

- Everything runs locally or on your own Render instance
- Raw messages are never logged or sent anywhere except OpenAI for embeddings/completions
- `/data` DELETE endpoint wipes all stored vectors and analytics
- `.gitignore` excludes `messages.json` and the raw chat file
