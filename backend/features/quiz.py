"""
Quiz mode — multi-query + month spread retrieval for fresh questions every run.
Returns structured JSON with memory_snippet for post-reveal display.
"""

import json
import random
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_QUIZ, _fmt_date
from llm import call_llm
from config import settings

QUIZ_SEED_QUERIES = [
    "funny moment joke teasing laugh",
    "miss you sad emotional feeling",
    "fight argument sorry upset",
    "late night long conversation",
    "food plans hangout meet",
    "who texts first morning routine",
    "inside joke repeated phrase catchphrase",
    "compliment sweet caring moment",
    "work college stress daily life",
    "random wholesome unexpected moment",
    "jealous protective concern",
    "future plans dream together",
]


async def generate_quiz(analytics: dict, store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    mc   = analytics.get("message_count", {})
    init = analytics.get("initiations", {})
    rt   = analytics.get("response_time", {})
    emojis = list(analytics.get("top_emojis", {}).keys())[:3]

    # 5 random seeds → different material every run
    seeds  = random.sample(QUIZ_SEED_QUERIES, 5)
    chunks = store.multi_query(seeds, n_per_query=4)
    # Add 2-per-month spread for temporal variety
    spread = store.month_spread(per_month=1)
    all_chunks = chunks + spread
    random.shuffle(all_chunks)
    selected = all_chunks[:14]

    context = "\n\n---\n\n".join(
        f"[{_fmt_date(c.get('start_time', ''))}]\n{c['text']}"
        for c in selected
    )

    user_content = f"""Memories from {u1} and {u2}'s WhatsApp chats (dates shown):
{context}

Stats:
- {u1}: {mc.get(u1, 0):,} messages, started {init.get(u1, 0)} conversations
- {u2}: {mc.get(u2, 0):,} messages, started {init.get(u2, 0)} conversations
- Median response time: {rt.get('median_seconds', 0)}s
- Top emojis: {' '.join(emojis)}

Generate 5 quiz questions. Rules:
- Every question must be based on something SPECIFIC in the memories above — reference the date
- Mix of types: stats-based, quote-based, behaviour-based, pattern-based
- Wrong options must be plausible but clearly wrong to someone who was there
- memory_snippet: copy an actual line from the memory the question is based on
- explanation: casual, like texting a friend, mention the date

Return ONLY valid JSON:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["A", "B", "C", "D"],
      "answer": "exact correct option text",
      "memory_snippet": "actual quoted line from the memory",
      "explanation": "casual explanation with date reference"
    }}
  ]
}}"""

    raw = await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_QUIZ}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.1)

    try:
        cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {"questions": [], "raw": raw, "error": "Could not parse JSON"}
