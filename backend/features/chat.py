"""
Chat mode — standard RAG chatbot with streaming.
"""

import json
from typing import AsyncGenerator
from embeddings import EmbeddingStore
from rag import build_context, build_messages
from llm import stream_llm


async def stream_chat(
    message: str, asking_user: str, store: EmbeddingStore
) -> AsyncGenerator[str, None]:
    """
    Retrieve relevant memories, call GPT-4.1 with streaming,
    yield SSE-formatted data chunks.
    """
    chunks = store.query(message)
    context = build_context(chunks)
    messages = build_messages(message, context, asking_user)

    async for token in stream_llm(messages):
        yield f"data: {json.dumps({'content': token})}\n\n"

    yield "data: [DONE]\n\n"
