"""
FastAPI application — all API routes for the Couple Chatbot.
"""

import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from config import settings
from data_processor import process_whatsapp_chat, save_messages
from embeddings import EmbeddingStore
from analytics import compute_analytics, load_analytics
from features.chat import stream_chat
from features.roast import generate_roast
from features.quiz import generate_quiz
from features.timeline import generate_timeline
from features.story import generate_story

app = FastAPI(title="Couple Chatbot API", version="1.0.0")

# Build origins list — FRONTEND_URL lets you add your exact Vercel URL
_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://*.vercel.app",
]
if os.getenv("FRONTEND_URL"):
    _origins.append(os.getenv("FRONTEND_URL"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Single shared instance — persisted to disk via Chroma
store = EmbeddingStore()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    message: str
    user: str = settings.user1_name


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": settings.model_name,
        "chat_loaded": not store.is_empty(),
    }


@app.post("/upload")
async def upload_chat(file: UploadFile = File(...)):
    """
    Upload a WhatsApp .txt export.
    Parses, embeds, and stores all messages. Returns basic stats.
    """
    if not file.filename.endswith(".txt"):
        raise HTTPException(400, "Only .txt files are supported")

    content = await file.read()
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("utf-8", errors="replace")

    messages = process_whatsapp_chat(text)
    if not messages:
        raise HTTPException(422, "No messages found. Check the file format.")

    save_messages(messages)
    chunk_count = store.store_messages(messages)
    analytics = compute_analytics(messages)

    return {
        "status": "ok",
        "message_count": len(messages),
        "chunk_count": chunk_count,
        "analytics_summary": {
            "total": analytics.get("total_messages"),
            "by_user": analytics.get("message_count"),
        },
    }


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Chat mode — streams GPT-4.1 response via SSE.
    Frontend reads this as text/event-stream.
    """
    if store.is_empty():
        raise HTTPException(400, "No chat data loaded. Upload a WhatsApp export first.")

    return StreamingResponse(
        stream_chat(req.message, req.user, store),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/roast")
async def roast(target: str = Query(default="both", description="'Shivang', 'Krishna', or 'both'")):
    """Roast mode — generates a funny roast based on chat stats."""
    analytics = load_analytics()
    if not analytics:
        raise HTTPException(400, "No analytics found. Upload a WhatsApp export first.")

    result = await generate_roast(analytics, target, store)
    return {"roast": result, "target": target}


@app.get("/quiz")
async def quiz():
    """Quiz mode — generates relationship trivia questions."""
    analytics = load_analytics()
    if not analytics:
        raise HTTPException(400, "No analytics found. Upload a WhatsApp export first.")

    result = await generate_quiz(analytics, store)
    return result


@app.get("/timeline")
async def timeline():
    """Timeline mode — generates a narrative relationship timeline."""
    if store.is_empty():
        raise HTTPException(400, "No chat data loaded. Upload a WhatsApp export first.")

    result = await generate_timeline(store)
    return result


@app.get("/story")
async def story(
    style: str = Query(
        default="romantic",
        description="Story style: romantic | poem | bollywood | roast_story | fairy_tale",
    )
):
    """Story mode — generates a creative piece about the couple."""
    if store.is_empty():
        raise HTTPException(400, "No chat data loaded. Upload a WhatsApp export first.")

    result = await generate_story(store, style)
    return {"story": result, "style": style}


@app.get("/analytics")
async def get_analytics():
    """Return full analytics JSON."""
    data = load_analytics()
    if not data:
        raise HTTPException(404, "No analytics found. Upload a WhatsApp export first.")
    return data


@app.delete("/data")
async def delete_data():
    """Privacy endpoint — wipe all stored data."""
    store.clear()
    for path in [settings.analytics_file, f"{settings.data_dir}/messages.json"]:
        if os.path.exists(path):
            os.remove(path)
    return {"status": "deleted", "message": "All data has been wiped 🗑️"}
