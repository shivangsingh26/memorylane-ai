"""
Roast mode — generates a funny, friendly roast based on chat analytics + sample memories.
"""

from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, build_context
from llm import call_llm
from config import settings


def _build_roast_prompt(analytics: dict, target: str, context: str) -> list[dict]:
    u1, u2 = settings.user1_name, settings.user2_name
    mc = analytics.get("message_count", {})
    rt = analytics.get("response_time", {})
    init = analytics.get("initiations", {})
    pct = analytics.get("message_percentage", {})
    emojis = list(analytics.get("top_emojis", {}).keys())[:5]

    stats_block = f"""
📊 Raw stats:
- Total messages: {analytics.get('total_messages', '?')}
- {u1}: {mc.get(u1, 0)} messages ({pct.get(u1, 0)}%)
- {u2}: {mc.get(u2, 0)} messages ({pct.get(u2, 0)}%)
- Avg response time: {_fmt_time(rt.get('avg_seconds', 0))}
- Median response time: {_fmt_time(rt.get('median_seconds', 0))}
- {u1} initiated conversations: {init.get(u1, 0)} times
- {u2} initiated conversations: {init.get(u2, 0)} times
- Top emojis used together: {' '.join(emojis) if emojis else 'none found'}
""".strip()

    top_words_u1 = list(analytics.get("top_words", {}).get(u1, {}).keys())[:5]
    top_words_u2 = list(analytics.get("top_words", {}).get(u2, {}).keys())[:5]
    stats_block += f"\n- {u1}'s most used words: {', '.join(top_words_u1)}"
    stats_block += f"\n- {u2}'s most used words: {', '.join(top_words_u2)}"

    if target == u1:
        target_line = f"Roast {u1} specifically — go hard on the 🤡 energy. Be funny and specific."
    elif target == u2:
        target_line = f"Roast {u2} specifically — be playful and sweet about it."
    else:
        target_line = f"Roast BOTH {u1} and {u2} equally — balance it out, be fair in your savagery 😂"

    memories_section = (
        f"\n\nHere are some actual memories from their chats:\n\n{context}"
        if context and "No relevant" not in context
        else ""
    )

    user_content = f"""
Based on these stats from {u1} and {u2}'s WhatsApp chat history:

{stats_block}
{memories_section}

Generate a hilarious, friendly roast. Rules:
- Reference SPECIFIC stats and memories — no generic jokes
- {target_line}
- Use emojis liberally 😂🔥
- Keep it between 150-250 words
- End with a sweet note — roast with love 💕
- Write in a mix of English and Hinglish (like they do) if it adds flavor
""".strip()

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]


def _fmt_time(seconds: int) -> str:
    if not seconds:
        return "N/A"
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds // 3600}h {(seconds % 3600) // 60}m"


async def generate_roast(analytics: dict, target: str, store: EmbeddingStore) -> str:
    # Get a few sample memories for flavor
    sample_chunks = store.sample_chunks(n=8)
    context = build_context(sample_chunks)
    messages = _build_roast_prompt(analytics, target, context)
    return await call_llm(messages)
