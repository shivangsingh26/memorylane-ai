"""
Timeline mode — strict chronological spread across 5 time periods
so the timeline actually covers the full arc of the relationship,
not just the first month of chats.
"""

import json
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_TIMELINE
from llm import call_llm
from config import settings


async def generate_timeline(store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    # 5 periods × 4 chunks each = 20 chunks spread across the full timeline
    chunks = store.temporal_spread(n_periods=5, per_period=4)

    context = "\n\n---\n\n".join(
        f"[{c.get('start_time', '')[:10]}]\n{c['text']}"
        for c in chunks
    )

    user_content = f"""These are real messages from {u1} and {u2}'s WhatsApp history,
sampled from different points across their entire relationship:

{context}

Analyze the emotional arc — how did their dynamic change over time?
Look for: tone shifts, vocabulary changes, frequency changes, emotional openness, inside jokes forming.

Write a relationship timeline as JSON:
{{
  "phases": [
    {{
      "name": "phase name that feels real, not generic",
      "period": "approximate time period",
      "vibe": "one honest sentence about the energy during this phase",
      "description": "2-3 sentences — specific, story-like, references actual content from the chats",
      "key_moment": "one actual quote or real moment from this phase"
    }}
  ],
  "overall_summary": "3-4 sentences told like a story, warm and specific, no generic lines",
  "fun_facts": [
    "specific fun fact from the actual chats",
    "another specific one",
    "one more"
  ]
}}

Be honest about what the chats actually show — including the mundane stuff, that's what makes it real.
Return ONLY valid JSON, no markdown."""

    raw = await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_TIMELINE}"},
        {"role": "user",   "content": user_content},
    ], temperature=0.95)

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"phases": [], "overall_summary": raw, "error": "Could not parse JSON"}
