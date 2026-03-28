"""
Timeline generator — identifies phases in the relationship and outputs a narrative.
"""

import json
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT
from llm import call_llm
from config import settings


async def generate_timeline(store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    # Pull chunks chronologically (first 10 + last 10 + middle 10)
    all_chunks = store.sample_chunks(n=30)
    context = "\n\n---\n\n".join(
        f"[{c.get('start_time', '')[:10]}]\n{c['text']}" for c in all_chunks
    )

    user_content = f"""
You have access to snippets from {u1} and {u2}'s entire WhatsApp chat history spanning multiple months.

Here are samples from across their conversation history:

{context}

Analyze these messages and write a beautiful relationship timeline. Structure it as JSON:

{{
  "phases": [
    {{
      "name": "Phase name (e.g. 'The Spark', 'Getting Comfortable', 'Deep Bond')",
      "period": "Approximate time period (e.g. 'Early days', 'Mid conversation', 'Recent')",
      "vibe": "One-line emotional vibe (e.g. 'Playful and curious 💫')",
      "description": "2-3 sentences describing this phase with specific examples from the chats",
      "key_moment": "One memorable quote or moment from this phase"
    }}
  ],
  "overall_summary": "A 3-4 sentence poetic summary of their journey together",
  "fun_facts": [
    "Specific fun fact 1 from the chats",
    "Specific fun fact 2",
    "Specific fun fact 3"
  ]
}}

Make it feel like a love story — because it is one. Be specific, warm, and use actual content from their chats.
Return ONLY valid JSON — no markdown, no extra text.
""".strip()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    raw = await call_llm(messages)

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"phases": [], "overall_summary": raw, "error": "Could not parse JSON — see overall_summary"}
