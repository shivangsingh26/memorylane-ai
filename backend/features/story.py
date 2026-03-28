"""
Story mode — emotionally targeted queries pull the richest material
(funny, sweet, dramatic moments) rather than random early chunks.
"""

import random
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_STORY, build_context
from llm import call_llm
from config import settings

STYLE_PROMPTS = {
    "romantic": (
        "Write a heartfelt short story (300-400 words) about their love story. "
        "Use specific moments and their actual dynamic — {u1}'s detached-but-not-really energy, "
        "{u2}'s expressiveness. Make it feel like it's genuinely them, not a template."
    ),
    "poem": (
        "Write a poem (12-16 lines) that captures their actual relationship energy — "
        "the banter, the warmth, the Hinglish, the 🤡 and 😭. Mix English and Hindi naturally. "
        "Reference real moments and phrases from their chats."
    ),
    "bollywood": (
        "Write a dramatic Bollywood-style narration about their love story. "
        "Overdramatic, filmy, use actual dialogue from their chats as movie lines. "
        "Include a villain (could be slow replies 😂), a climax, a resolution. Be hilarious."
    ),
    "roast_story": (
        "Write a story called 'How These Two Actually Text' — narrate their relationship "
        "as if exposing them to the world. Use their real habits, phrases, response patterns. "
        "Gently savage. Should make them both laugh AND cringe."
    ),
    "fairy_tale": (
        "Write a fairy tale beginning with 'Once upon a time...' but set in the real world — "
        "WhatsApp read receipts, blue ticks, 'noob', '😭😭', 'acha'. Use their actual dynamic. "
        "Make the mundane magical."
    ),
}

# Emotional seed queries per style — target the richest relevant memories
STYLE_QUERIES = {
    "romantic":    ["miss you love sweet caring", "late night deep conversation", "first time wholesome moment"],
    "poem":        ["banter tease funny joke", "sweet emotional moment", "daily life routine together"],
    "bollywood":   ["dramatic moment fight sorry", "emotional confession feeling", "funny chaos situation"],
    "roast_story": ["acha noob teasing response", "slow reply ignored message", "clown moment embarrassing"],
    "fairy_tale":  ["good morning routine daily", "wholesome moment caring", "funny unexpected moment"],
}


async def generate_story(store: EmbeddingStore, style: str = "romantic") -> str:
    u1, u2 = settings.user1_name, settings.user2_name

    queries = STYLE_QUERIES.get(style, STYLE_QUERIES["romantic"])
    # Semantic search for emotionally relevant chunks
    semantic_chunks = store.multi_query(queries, n_per_query=3)
    # Add some random chunks for unexpected authentic detail
    random_chunks = store.random_sample(n=5)

    all_chunks = semantic_chunks + random_chunks
    random.shuffle(all_chunks)
    context = build_context(all_chunks[:10])

    style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["romantic"]).format(u1=u1, u2=u2)

    user_content = f"""Real memories from {u1} and {u2}'s WhatsApp chats:

{context}

{style_instruction}

Rules:
- Use SPECIFIC details from the memories above — exact phrases, situations, dynamics
- Don't just use their names in a generic story — make it feel like IT'S THEM
- No AI-sounding phrases like "a tapestry of emotions" or "their journey together"
- Write it and stop. No preamble, no "Here is your story:", just begin."""

    return await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_STORY}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.05)
