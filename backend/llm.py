"""
OpenAI LLM wrapper using gpt-4.1.
Supports both full response and SSE streaming.
"""

from typing import AsyncGenerator
from openai import AsyncOpenAI
from config import settings


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def call_llm(messages: list[dict]) -> str:
    """Return the full response string from GPT-4.1."""
    response = await _client().chat.completions.create(
        model=settings.model_name,
        messages=messages,
        temperature=0.9,
    )
    return response.choices[0].message.content


async def stream_llm(messages: list[dict]) -> AsyncGenerator[str, None]:
    """Yield content chunks from a streaming GPT-4.1 call."""
    stream = await _client().chat.completions.create(
        model=settings.model_name,
        messages=messages,
        temperature=0.9,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
