# Changelog

All changes to MemoryLane AI, documented chronologically.

---

## [v0.4] — 2026-03-29 · Retrieval Quality + Output Realism Overhaul

**Goal:** Stop hallucinated outputs, fix retrieval bias toward Oct 2025, make responses sound human.

### Backend — Embeddings (`embeddings.py`)
- **NEW: `month_spread()`** — samples chunks from every calendar month equally. Replaces `temporal_spread()` which was broken because Oct 2025 (42% of all chunks) dominated 2-3 of 5 time periods
- **NEW: month index cache** — builds a `month → [chunk_ids]` mapping once and caches it, making month-aware sampling fast
- **FIXED: `random_sample()`** — now samples randomly across months first, then chunks within months. Previously always returned chunks from the same offset window
- **FIXED: `mmr_query()`** — no changes to algorithm, but now used correctly across all features
- **REMOVED: `temporal_spread()`** — replaced entirely by `month_spread()`

### Backend — RAG (`rag.py`)
- **NEW: Date injection** — every chunk shown to the LLM now includes a human-readable date label ("October 15, 2025") via `_fmt_date()`. Previously the LLM had no idea when things happened, causing timeline and story hallucinations
- **NEW: Grounding instruction** — system prompt now explicitly tells the LLM: "only reference what you can see in the memories provided"
- **NEW: Emoji control** — hard limit of 2-3 emojis per entire response. Previously "use emojis naturally" caused one emoji per sentence
- **REWRITTEN: System prompt** — removed all vague personality descriptors, replaced with specific behavioral rules: no bullet points, no headers, no "their bond" / "journey together" phrases, max 2-3 emojis
- **NEW: Per-feature tone constants** — `TONE_CHAT`, `TONE_ROAST`, `TONE_QUIZ`, `TONE_TIMELINE`, `TONE_STORY` each explicitly define what "good output" looks like for that feature

### Backend — Features

**`features/chat.py`**
- Now uses `mmr_query()` (relevant + diverse) instead of basic `query()`
- Emits source dates as first SSE event (`{"sources": [...]}`) for frontend attribution

**`features/roast.py`**
- Now uses `month_spread(per_month=2)` — roast material sampled from all 9 months
- **NEW structured output**: returns JSON with `sections[]`, `verdict`, `save` instead of a single text blob
- Temperature raised to `1.0` for more creative output

**`features/quiz.py`**
- Now uses `multi_query()` with 5 randomly-selected seeds from a pool of 12, ensuring different questions every run
- Adds `month_spread(per_month=1)` for temporal variety alongside semantic results
- **NEW field: `memory_snippet`** — actual quoted line from the memory the question is based on
- Temperature raised to `1.1`

**`features/timeline.py`**
- Now uses `month_spread(per_month=3)` — 3 chunks from each of 9 months = ~27 chronologically spread chunks
- **NEW field: `date_range`** replaces generic `period` — actual calendar dates from the memories
- LLM instructed to only create phases for time periods it has actual data for

**`features/story.py`**
- Emotional seed queries per style (e.g. romantic → "miss you love sweet caring") target the richest relevant memories
- Adds `month_spread(per_month=1)` for unexpected authentic detail
- LLM explicitly told: "no AI phrases: tapestry of emotions, their bond, journey together"
- Temperature raised to `1.05`

### Frontend — Components

**`lib/api.ts`**
- `streamChat()` return type changed from `AsyncGenerator<string>` to `AsyncGenerator<ChatChunk>` where `ChatChunk = string | { sources: string[] }`
- Generator now yields source objects when `{"sources": [...]}` SSE event arrives

**`components/modes/ChatMode.tsx`**
- Source dates shown subtly below each bot response ("Based on memories from Oct 2025, Feb 2026")
- Handles both string tokens and source objects from the updated stream

**`components/modes/RoastMode.tsx`**
- Renders new structured JSON: 3 labeled section cards + verdict card + warm close
- Each section has a distinct accent color (Numbers=cyan, Caught In 4K=orange, Habit=pink)

**`components/modes/QuizMode.tsx`**
- Shows `memory_snippet` as a quoted block after reveal, before the explanation
- Cleaner done screen copy

**`components/modes/TimelineMode.tsx`**
- Renders `date_range` from backend (actual dates like "Sep 2025 – Oct 2025")
- Handles both old `period` and new `date_range` fields for backwards compatibility

**`components/modes/StoryMode.tsx`**
- Removed emoji from style picker, cleaner text-only labels
- Story body uses serif font at `text-[15px]` with `leading-[1.9]` for reading comfort
- Rewrite button moved inside the card header

---

## [v0.3] — 2026-03-28 · First Retrieval Quality Pass

**Goal:** Fix same-chunks-every-time problem, reduce robotic output.

### Backend
- **NEW: `mmr_query()`** in `embeddings.py` — Maximal Marginal Relevance retrieval. Picks chunks that are both relevant to the query AND diverse from each other. Controlled by `diversity` param (0=pure relevance, 1=pure diversity)
- **NEW: `multi_query()`** — runs multiple seed queries and deduplicates results by text prefix
- **FIXED: `random_sample()`** — added random offset so it doesn't always return first N chunks
- **FIXED: `temporal_spread()`** — divided collection by chunk index into N equal buckets (later replaced in v0.4 by `month_spread()` which is more accurate)
- **Rewritten system prompt** — first pass at human-sounding tone, banned bullet points
- **Per-feature temperature** — chat=0.85, story/roast/quiz=1.0-1.1
- **`llm.py`** — `temperature` parameter added to both `call_llm()` and `stream_llm()`

---

## [v0.2] — 2026-03-28 · Full Frontend + Deployment

### Frontend (Next.js 14)
- **Design system** — "Midnight Studio" dark theme (`#070711` base), glassmorphism cards, violet→pink gradient
- **`globals.css`** — custom CSS variables, glass/glow classes, bubble styles, timeline connector, dot-pulse animation, cursor-blink for streaming
- **`Sidebar.tsx`** — mode navigation with icons, locks non-chat modes until data is loaded
- **`Header.tsx`** — user switcher (Shivang/Krishna), upload button, clear data button
- **`UploadModal.tsx`** — drag-and-drop file upload with progress bar, auto-closes on success
- **`ChatMode.tsx`** — streaming chat with suggested prompts, user/bot bubbles, loading dots
- **`RoastMode.tsx`** — target picker + animated reveal card
- **`QuizMode.tsx`** — 5 questions, option picker, reveal + explanation, score tracker, done screen
- **`TimelineMode.tsx`** — vertical timeline with glowing connector line, phase cards with key quote
- **`StoryMode.tsx`** — 5 style presets, serif body text
- **`AnalyticsMode.tsx`** — message count bars, emoji cloud, word frequency bars, monthly activity chart
- **`lib/api.ts`** — typed API client for all 8 endpoints + streaming generator
- **`next.config.mjs`** — rewrites `/api/*` to backend URL (env-configurable for Vercel)

### Deployment
- **`backend/Dockerfile`** — Python 3.12-slim, installs deps, copies baked data, serves on `$PORT`
- **`render.yaml`** — Render web service config, Docker runtime, free plan
- **`frontend/vercel.json`** — Vercel build config
- **`.gitignore`** — excludes `.env`, `_chat.txt`, `messages.json`, tracks `data/chroma/` and `analytics.json`
- **Deployed**: backend on Render, frontend on Vercel via CLI (`vercel --prod`)
- **CORS** — `FRONTEND_URL` env var lets backend accept requests from exact Vercel domain

---

## [v0.1] — 2026-03-27 · Backend Foundation

### Data Processing (`data_processor.py`)
- Parser for WhatsApp iOS export format: `[DD/MM/YY, HH:MM:SS AM/PM] Sender: message`
- Android format fallback supported
- Strips media omitted, system messages, deleted messages
- Normalizes sender names: "Krishna❤️" → "Krishna", "Shivang Singh" → "Shivang"
- Handles multi-line messages (continuation lines appended to previous)
- Chunker: groups messages into 7-message chunks preserving conversational context
- Result: 85,411 messages → 12,202 chunks

### Vector Store (`embeddings.py`)
- ChromaDB persistent client with cosine similarity
- Batch upsert (50 chunks/batch) with rate-limit sleep
- `text-embedding-3-small` via OpenAI API

### RAG Pipeline (`rag.py`)
- System prompt with personality: playful best-friend voice, Hinglish-aware
- Context builder formats chunks for LLM consumption

### Analytics Engine (`analytics.py`)
- Message count and percentage per user
- Emoji frequency (top 15)
- Word frequency per user (with stop word filtering, English + Hinglish)
- Response time stats (avg, median, min, max — capped at 6h for meaningful responses)
- Conversation initiation count (gap > 3h = new initiation)
- Activity by hour (24-slot array per user)
- Messages by month

### LLM (`llm.py`)
- OpenAI async wrapper for `gpt-5.1`
- `call_llm()` for full response, `stream_llm()` for SSE streaming

### Features
- **`chat.py`** — SSE streaming RAG chat
- **`roast.py`** — stats-based roast with temporal sample context
- **`quiz.py`** — 5-question JSON quiz from chat memories
- **`timeline.py`** — chronological relationship phases as JSON
- **`story.py`** — 5 styles: romantic, poem, bollywood, roast_story, fairy_tale

### API (`main.py`)
- `POST /upload` — parse + embed WhatsApp .txt
- `POST /chat` — streaming SSE chat
- `GET /roast?target=` — roast generation
- `GET /quiz` — quiz generation
- `GET /timeline` — timeline generation
- `GET /story?style=` — story generation
- `GET /analytics` — full stats JSON
- `DELETE /data` — wipe all stored data + vectors

### Config (`config.py`, `pyproject.toml`, `.env.example`)
- `pydantic-settings` for env-based config
- Model: `gpt-5.1`, embeddings: `text-embedding-3-small`
- Configurable: user names, chunk size, RAG top-k

---

## Stats

| Metric | Value |
|--------|-------|
| Total messages parsed | 85,411 |
| Chunks embedded | 12,202 |
| Months of data | 9 (Jun 2025 – Mar 2026) |
| Peak month | Oct 2025 (5,107 chunks, 42%) |
| Embedding model | text-embedding-3-small |
| LLM | gpt-5.1 |
| Vector DB | ChromaDB (local, cosine similarity) |
| Frontend | Next.js 14, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Hosting | Vercel (frontend) + Render (backend) |
