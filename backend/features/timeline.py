"""
Timeline mode — month_spread gives one chunk per calendar month so the
timeline accurately reflects the actual arc, not just the peak-volume months.
"""

import json
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_TIMELINE, _fmt_date
from llm import call_llm
from config import settings


async def generate_timeline(store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    # 3 chunks per month across all 9 months = ~27 chunks, chronologically spread
    chunks = store.month_spread(per_month=3)

    context = "\n\n---\n\n".join(
        f"[{_fmt_date(c.get('start_time', ''))}]\n{c['text']}"
        for c in chunks
    )

    user_content = f"""These are real messages from {u1} and {u2}'s WhatsApp, sampled from every month of their history:

{context}

Look at how the dynamic changes month by month — tone, vocabulary, what they talk about, emotional openness, response energy.

Return a relationship timeline as JSON:
{{
  "phases": [
    {{
      "name": "a specific phase name that reflects what actually happened — not generic like 'The Beginning'",
      "date_range": "Month Year – Month Year (use actual dates from the memories)",
      "vibe": "one honest sentence about the energy in this phase — based on what you actually see",
      "description": "2-3 sentences, narrative style, referencing specific things from the memories with dates",
      "key_quote": "an actual line from one of the memories in this phase — copy it exactly"
    }}
  ],
  "overall_summary": "3-4 sentences told as a story — specific, honest, no generic 'their bond grew stronger' lines",
  "fun_facts": [
    "a specific verifiable fact from the chats with a date",
    "another one",
    "one more"
  ]
}}

Only create phases for time periods you actually have memories for.
Use exact dates. Don't invent events not in the memories.
Return ONLY valid JSON."""

    raw = await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_TIMELINE}"},
        {"role": "user",   "content": user_content},
    ], temperature=0.9)

    try:
        cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"phases": [], "overall_summary": raw, "error": "Could not parse JSON"}
