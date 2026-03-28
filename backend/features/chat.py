"""
Chat mode — MMR retrieval + streaming.
MMR ensures retrieved chunks are both relevant AND diverse,
so the bot doesn't just quote the same conversation 5 times.
"""

import json
from typing import AsyncGenerator
from embeddings import EmbeddingStore
from rag import build_context, build_messages, TONE_CHAT
from llm import stream_llm


async def stream_chat(
    message: str, asking_user: str, store: EmbeddingStore
) -> AsyncGenerator[str, None]:
    # MMR: relevant to the question but diverse across time
    chunks  = store.mmr_query(message, n_results=6, fetch_k=30, diversity=0.55)
    context = build_context(chunks)
    messages = build_messages(message, context, asking_user, tone=TONE_CHAT)

    async for token in stream_llm(messages):
        yield f"data: {json.dumps({'content': token})}\n\n"

    yield "data: [DONE]\n\n"
