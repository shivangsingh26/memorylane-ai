<div align="center">

```
███╗   ███╗███████╗███╗   ███╗ ██████╗ ██████╗ ██╗   ██╗██╗      █████╗ ███╗   ██╗███████╗
████╗ ████║██╔════╝████╗ ████║██╔═══██╗██╔══██╗╚██╗ ██╔╝██║     ██╔══██╗████╗  ██║██╔════╝
██╔████╔██║█████╗  ██╔████╔██║██║   ██║██████╔╝ ╚████╔╝ ██║     ███████║██╔██╗ ██║█████╗
██║╚██╔╝██║██╔══╝  ██║╚██╔╝██║██║   ██║██╔══██╗  ╚██╔╝  ██║     ██╔══██║██║╚██╗██║██╔══╝
██║ ╚═╝ ██║███████╗██║ ╚═╝ ██║╚██████╔╝██║  ██║   ██║   ███████╗██║  ██║██║ ╚████║███████╗
╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝
                                    A  I
```

**An AI that remembers your relationship better than you do.**

Feed it your WhatsApp history. It will chat about your memories, roast you with real stats,
quiz you on moments you forgot, map your entire relationship arc, and write poetry about you two.

---

![Next.js](https://img.shields.io/badge/Next.js_14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python_3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/GPT--5.1-412991?style=for-the-badge&logo=openai&logoColor=white)
![Vercel](https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)
![Render](https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=black)

</div>

---

## What is this?

You exported your WhatsApp chat with your partner — 85,000+ messages, 9 months of inside jokes, arguments, late-night conversations, and random "hehe"s. That's a goldmine of actual memories sitting in a `.txt` file.

MemoryLane AI ingests all of it. It embeds every message into a vector database and wraps a GPT-5.1 agent around it that knows your relationship intimately. Not a generic chatbot — it speaks about *your* specific moments, pulls *your* actual phrases, and roasts you with *your* real stats.

---

## Modes

<table>
<tr>
<td width="50%">

### 💬 Chat
Ask anything. *"Who apologizes first when you fight?"*, *"What was that trip we talked about?"*, *"What does she say when she's actually upset vs pretending not to be?"*

RAG retrieves the exact relevant chunks. GPT-5.1 answers like a friend who read every message — not like a chatbot.

</td>
<td width="50%">

### 🔥 Roast
Real stats. Real receipts.

Who texts first more. Who says "I'm fine" and clearly isn't. Who uses the most emojis. Response time averages. Most-used phrases. All weaponized against you.

</td>
</tr>
<tr>
<td width="50%">

### 🧠 Quiz
Auto-generated trivia from your actual chat history.

*"What did she say when you forgot to reply for 6 hours?"*
*"Which month had the most messages?"*
*"What's the phrase that appears 47 times?"*

</td>
<td width="50%">

### 💫 Timeline
Your relationship broken into phases — the early awkwardness, the point things shifted, the inside jokes that emerged, the rough patches, where you are now.

A narrative built entirely from message patterns and content.

</td>
</tr>
<tr>
<td width="50%">

### ✍️ Story
Writes something about you two. A story. A poem. A Bollywood script. A horror story where the villain is your response time.

Style is yours to choose.

</td>
<td width="50%">

### 📊 Analytics
The numbers dashboard.

Message counts per person · emoji frequency · response time distribution · monthly activity heatmap · most active hours · longest dry spells.

</td>
</tr>
</table>

---

## How it works

```
  WhatsApp .txt export (85k+ messages, 9 months)
              │
              ▼
  ┌─────────────────────────┐
  │   Parse + Clean         │  Removes media/system msgs · keeps emojis · preserves timestamps
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │   Chunk (7 msgs/chunk)  │  12,202 chunks · preserves conversational context
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │   Embed + Store         │  text-embedding-3-small → ChromaDB (local, baked into deploy)
  └────────────┬────────────┘
               │
         User query
               │
               ▼
  ┌─────────────────────────┐
  │   RAG Retrieval         │  MMR retrieval · temporal spread · top-K chunks with dates
  └────────────┬────────────┘
               │
               ▼
  ┌─────────────────────────┐
  │   GPT-5.1 + Personality │  Date-grounded · anti-hallucination · Hinglish-aware
  └────────────┬────────────┘
               │
               ▼
       Streamed response
```

**Key design decisions:**
- Every chunk is date-stamped before embedding so the LLM can say *"this happened in March"* accurately
- MMR (Maximal Marginal Relevance) retrieval ensures temporal spread — not just the 5 most similar chunks but chunks from across the relationship
- Structured outputs for Quiz/Timeline prevent hallucinated JSON
- Per-feature temperature tuning — Chat is grounded, Story is creative, Roast is chaotic

---

## Tech Stack

```
┌──────────────────────────────────────────────────────────┐
│  FRONTEND                                                │
│  Next.js 14 (App Router) · TypeScript · Tailwind CSS    │
│  Deployed on Vercel                                      │
├──────────────────────────────────────────────────────────┤
│  BACKEND                                                 │
│  FastAPI · Python 3.12 · Uvicorn                        │
│  Deployed on Render (Docker)                             │
├──────────────────────────────────────────────────────────┤
│  AI                                                      │
│  OpenAI GPT-5.1 (completions, streaming)                │
│  text-embedding-3-small (embeddings)                     │
├──────────────────────────────────────────────────────────┤
│  VECTOR DB                                               │
│  ChromaDB (local, baked into the Docker image)          │
└──────────────────────────────────────────────────────────┘
```

---

## Local Setup

**Prerequisites:** Python 3.11+, Node.js 18+, OpenAI API key

### 1. Backend

```bash
cd backend

# Create and activate virtualenv
python3 -m venv .venv && source .venv/bin/activate

# Install dependencies
pip install fastapi "uvicorn[standard]" pydantic-settings "openai>=1.55" "chromadb>=0.5" python-multipart

# Configure environment
cp .env.example .env
# Edit .env → set OPENAI_API_KEY=sk-...

# Start the API server
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd frontend

npm install

# Point at your local backend
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

npm run dev
# → http://localhost:3000
```

### 3. Load your chat data

1. Open WhatsApp → your chat → **⋮ → More → Export Chat → Without Media**
2. Go to `http://localhost:3000` → click **Upload Chat**
3. Drop the `.txt` file — embeddings generate in ~2–3 minutes for large chats

---

## Project Structure

```
couple-chatbot/
├── backend/
│   ├── main.py              # FastAPI app + all routes
│   ├── config.py            # Settings (pydantic-settings)
│   ├── data_processor.py    # WhatsApp parser + chunker
│   ├── embeddings.py        # ChromaDB vector store (MMR retrieval)
│   ├── rag.py               # Context builder + personality prompt
│   ├── analytics.py         # Stats engine
│   ├── llm.py               # OpenAI wrapper (streaming)
│   ├── features/
│   │   ├── chat.py          # Streaming RAG chat
│   │   ├── roast.py         # Roast generator
│   │   ├── quiz.py          # Quiz generator (structured output)
│   │   ├── timeline.py      # Timeline generator (structured output)
│   │   └── story.py         # Story/poem/script generator
│   ├── data/                # Baked ChromaDB + analytics cache
│   └── Dockerfile
│
├── frontend/
│   ├── app/                 # Next.js App Router
│   ├── components/
│   │   ├── modes/           # ChatMode · RoastMode · QuizMode · TimelineMode · StoryMode · AnalyticsMode
│   │   └── ui/              # GlassCard · Sidebar · Header · Upload modal · LoadingDots
│   └── lib/
│       └── api.ts           # Typed API client
│
└── render.yaml              # Render deployment config (auto-detected)
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload WhatsApp `.txt` → parse + embed |
| `POST` | `/chat` | Streaming RAG chat (SSE) |
| `GET` | `/roast` | Generate roast from real stats |
| `GET` | `/quiz` | Auto-generate relationship trivia |
| `GET` | `/timeline` | Build relationship phases narrative |
| `GET` | `/story` | Write story/poem in chosen style |
| `GET` | `/analytics` | Full stats JSON |
| `GET` | `/health` | Service health + model info |
| `DELETE` | `/data` | Wipe all stored vectors + analytics |

---

## Deployment

### Frontend → Vercel

```bash
# In Vercel dashboard or CLI
Root Directory:  frontend
Build Command:   npm run build
Output Dir:      .next

# Environment variable
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

### Backend → Render

`render.yaml` is included — Render auto-detects it. Set one env var:

```bash
OPENAI_API_KEY=sk-...
```

The ChromaDB embeddings are baked into the Docker image. No re-embedding at runtime.

---

## Privacy

- Everything runs on your own infrastructure (Vercel + your Render instance)
- Raw messages are only sent to OpenAI for embedding and completions — same as using ChatGPT
- The `/data` DELETE endpoint wipes all stored vectors and analytics cache instantly
- `messages.json` and raw chat exports are in `.gitignore` — they never touch your repo

---

<div align="center">

Built for two people who text too much.

</div>
