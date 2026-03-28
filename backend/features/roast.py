"""
Roast mode — temporal spread retrieval so the roast covers the full
relationship arc, not just the first few weeks of chats.
"""

from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_ROAST, build_context
from llm import call_llm
from config import settings


def _fmt_time(seconds: int) -> str:
    if not seconds:
        return "N/A"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


async def generate_roast(analytics: dict, target: str, store: EmbeddingStore) -> str:
    u1, u2 = settings.user1_name, settings.user2_name

    # Spread across 4 time periods so roast material isn't all from one era
    temporal_chunks = store.temporal_spread(n_periods=4, per_period=3)
    context = build_context(temporal_chunks)

    mc   = analytics.get("message_count", {})
    pct  = analytics.get("message_percentage", {})
    rt   = analytics.get("response_time", {})
    init = analytics.get("initiations", {})
    emojis     = list(analytics.get("top_emojis", {}).keys())[:5]
    words_u1   = list(analytics.get("top_words", {}).get(u1, {}).keys())[:6]
    words_u2   = list(analytics.get("top_words", {}).get(u2, {}).keys())[:6]

    if target == u1:
        target_line = f"Roast {u1} — lean into the 🤡 energy, the 'acha' responses, acting unbothered while clearly not being unbothered."
    elif target == u2:
        target_line = f"Roast {u2} — playful and sweet about it, the 😭 usage, the expressiveness."
    else:
        target_line = f"Roast both equally. Give each their moment."

    user_content = f"""Here's actual data from {u1} and {u2}'s WhatsApp history:

Stats:
- {u1}: {mc.get(u1, 0):,} messages ({pct.get(u1, 0)}%), started {init.get(u1, 0)} conversations
- {u2}: {mc.get(u2, 0):,} messages ({pct.get(u2, 0)}%), started {init.get(u2, 0)} conversations
- Average response time: {_fmt_time(rt.get('avg_seconds', 0))} | Median: {_fmt_time(rt.get('median_seconds', 0))}
- {u1}'s most used words: {', '.join(words_u1)}
- {u2}'s most used words: {', '.join(words_u2)}
- Top emojis between them: {' '.join(emojis)}

Actual memories from across their chat history:
{context}

{target_line}

Write a roast (150–220 words). Sound like a friend who's been watching these two for months —
amused, a little done with both of them, but genuinely fond. Use their actual phrases and patterns.
No headers. No lists. Just talk. Hinglish is fine. End with something warm."""

    return await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_ROAST}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.0)
