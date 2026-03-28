"""
Roast mode — structured JSON output with 3 sections + verdict + warm close.
Uses month_spread so roast material covers the full 9-month arc.
"""

import json
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_ROAST, build_context
from llm import call_llm
from config import settings


def _fmt_time(s: int) -> str:
    if not s:       return "N/A"
    if s < 60:      return f"{s}s"
    if s < 3600:    return f"{s // 60}m {s % 60}s"
    return f"{s // 3600}h {(s % 3600) // 60}m"


async def generate_roast(analytics: dict, target: str, store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    # Month spread — one sample from each of 9 months, 2 per month
    chunks  = store.month_spread(per_month=2)
    context = build_context(chunks)

    mc    = analytics.get("message_count", {})
    pct   = analytics.get("message_percentage", {})
    rt    = analytics.get("response_time", {})
    init  = analytics.get("initiations", {})
    emojis  = list(analytics.get("top_emojis", {}).keys())[:5]
    words_u1 = list(analytics.get("top_words", {}).get(u1, {}).keys())[:6]
    words_u2 = list(analytics.get("top_words", {}).get(u2, {}).keys())[:6]

    if target == u1:
        focus = (f"Focus on {u1}. Lean into: acting unbothered while clearly bothered, "
                 f"the 'acha'/'hehe'/'noob' vocabulary, the 2-word replies to long messages, "
                 f"calling himself unbothered while initiating {init.get(u1, 0)} conversations.")
    elif target == u2:
        focus = (f"Focus on {u2}. Lean into: the 😭 overuse, the expressiveness, "
                 f"sharing every small thing, the 'arre'/'haaaa' energy.")
    else:
        focus = f"Roast both equally — {u1} first, then {u2}. Be fair in the savagery."

    user_content = f"""Stats from {u1} and {u2}'s WhatsApp (9 months of data):

- {u1}: {mc.get(u1, 0):,} messages ({pct.get(u1, 0)}%), started {init.get(u1, 0)} conversations
- {u2}: {mc.get(u2, 0):,} messages ({pct.get(u2, 0)}%), started {init.get(u2, 0)} conversations
- Avg response time: {_fmt_time(rt.get('avg_seconds', 0))} | Median: {_fmt_time(rt.get('median_seconds', 0))}
- {u1}'s most used words: {', '.join(words_u1)}
- {u2}'s most used words: {', '.join(words_u2)}
- Top emojis: {' '.join(emojis)}

Real memories from across their chat history (with dates):
{context}

{focus}

Return structured JSON only — no markdown, no extra text:
{{
  "sections": [
    {{
      "label": "The Numbers",
      "text": "2-3 sentences about what the stats reveal — specific, with actual numbers, conversational tone"
    }},
    {{
      "label": "Caught In 4K",
      "text": "2-3 sentences calling out a specific pattern or moment from the memories with its date"
    }},
    {{
      "label": "The Habit",
      "text": "2-3 sentences about their recurring behaviour pattern — based only on what's in the memories"
    }}
  ],
  "verdict": "One savage one-liner that summarises the whole roast",
  "save": "One genuinely warm closing sentence — no sarcasm here"
}}"""

    raw = await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_ROAST}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.0)

    try:
        cleaned = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: wrap raw text in expected structure
        return {
            "sections": [{"label": "The Roast", "text": raw}],
            "verdict": "",
            "save": "",
        }
