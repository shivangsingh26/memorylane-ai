"""
Chat mode — MMR retrieval + streaming.
Returns SSE stream. Source dates passed separately for UI display.
"""

import json
from typing import AsyncGenerator
from embeddings import EmbeddingStore
from rag import build_context, build_messages, TONE_CHAT
from llm import stream_llm


async def stream_chat(
    message: str, asking_user: str, store: EmbeddingStore
) -> AsyncGenerator[str, None]:
    chunks  = store.mmr_query(message, n_results=6, fetch_k=30, diversity=0.55)
    context = build_context(chunks)
    msgs    = build_messages(message, context, asking_user, tone=TONE_CHAT)

    # Send source dates first so frontend can show them
    sources = [
        c["start_time"][:10] for c in chunks if c.get("start_time")
    ]
    yield f"data: {json.dumps({'sources': sources})}\n\n"

    async for token in stream_llm(msgs, temperature=0.85):
        yield f"data: {json.dumps({'content': token})}\n\n"

    yield "data: [DONE]\n\n"
