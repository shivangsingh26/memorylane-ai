"""
OpenAI LLM wrapper (gpt-5.1).
Supports full response and SSE streaming.
Temperature is per-call — different features use different values.
"""

from typing import AsyncGenerator
from openai import AsyncOpenAI
from config import settings


def _client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def call_llm(messages: list[dict], temperature: float = 0.9) -> str:
    """Return the full response string."""
    response = await _client().chat.completions.create(
        model=settings.model_name,
        messages=messages,
        temperature=temperature,
    )
    return response.choices[0].message.content


async def stream_llm(messages: list[dict], temperature: float = 0.85) -> AsyncGenerator[str, None]:
    """Yield content chunks from a streaming call."""
    stream = await _client().chat.completions.create(
        model=settings.model_name,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta
