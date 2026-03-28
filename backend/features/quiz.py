"""
Quiz mode — multi-query retrieval with a random temporal offset so questions
are different every single run, not recycled from the same early chunks.
"""

import json
import random
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_QUIZ
from llm import call_llm
from config import settings


# Diverse seed queries — each targets a different aspect of the relationship
QUIZ_SEED_QUERIES = [
    "funny moment joke teasing",
    "miss you sad emotional feelings",
    "fight argument sorry upset",
    "late night long conversation",
    "food plans hangout meet",
    "who texts first good morning",
    "inside joke repeated phrase",
    "compliment sweet caring moment",
    "work college study stress",
    "random wholesome daily life",
]


async def generate_quiz(analytics: dict, store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    mc   = analytics.get("message_count", {})
    init = analytics.get("initiations", {})
    rt   = analytics.get("response_time", {})
    emojis = list(analytics.get("top_emojis", {}).keys())[:3]

    # Pick 5 random seed queries so every quiz run hits different material
    seeds = random.sample(QUIZ_SEED_QUERIES, 5)
    chunks = store.multi_query(seeds, n_per_query=4)

    # Also sprinkle in some temporally-spread chunks for variety
    temporal = store.temporal_spread(n_periods=3, per_period=2)
    all_chunks = chunks + temporal

    # Format context — limit to 12 chunks to keep prompt focused
    random.shuffle(all_chunks)
    context_chunks = all_chunks[:12]
    context = "\n\n---\n\n".join(
        f"[{c.get('start_time','')[:10]}]\n{c['text']}"
        for c in context_chunks
    )

    user_content = f"""You have memories from {u1} and {u2}'s WhatsApp chats. Generate a relationship quiz.

Actual chat memories (different moments from across their history):
{context}

Quick stats to use:
- {u1} sent {mc.get(u1, '?'):,} messages, {u2} sent {mc.get(u2, '?'):,}
- {u1} started conversations {init.get(u1, '?')} times, {u2} started {init.get(u2, '?')} times
- Median response time: {rt.get('median_seconds', 0)} seconds
- Top emojis: {' '.join(emojis) if emojis else 'unknown'}

Generate exactly 5 quiz questions. Requirements:
- Every question must reference something SPECIFIC from the chat memories above
- Questions must be varied: mix stats-based, quote-based, behaviour-based, emoji-based
- Do NOT generate generic relationship questions — everything must be verifiable from the memories
- Wrong options should be plausible but clearly wrong to someone who knows the chats

Return ONLY valid JSON, no markdown, no extra text:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["A", "B", "C", "D"],
      "answer": "exact correct option text",
      "explanation": "casual explanation referencing the specific moment"
    }}
  ]
}}"""

    raw = await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_QUIZ}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.1)

    try:
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"questions": [], "raw": raw, "error": "Could not parse JSON"}
