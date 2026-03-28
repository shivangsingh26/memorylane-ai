"""
Story mode — emotionally targeted multi-query + random month samples.
Output is plain text — rich prose, no JSON.
"""

import random
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, TONE_STORY, build_context
from llm import call_llm
from config import settings

STYLE_PROMPTS = {
    "romantic": (
        "Write a heartfelt short story (300-400 words) about them. "
        "Use their actual dynamic — {u1}'s 2-word replies hiding real feelings, "
        "{u2}'s expressiveness. Use specific moments from the memories. "
        "Make it feel unmistakably like them, not a template with names swapped in."
    ),
    "poem": (
        "Write a poem (12-16 lines) that captures their actual energy — the banter, "
        "the warmth, the Hinglish, the specific phrases they use. "
        "Reference real moments with dates if possible. Mix Hindi and English naturally."
    ),
    "bollywood": (
        "Write a dramatic Bollywood-style narration. Use actual dialogue from the memories "
        "as movie lines. Create a dramatic arc — conflict, climax, resolution — "
        "all based on real things from the chats. Be over the top but grounded in what actually happened."
    ),
    "roast_story": (
        "Write a story called 'An Honest Account of How These Two Actually Text'. "
        "Narrate their texting patterns using specific moments and dates from the memories. "
        "Expose {u1}'s 'acha' responses and {u2}'s 😭 energy with affection. "
        "Make them both laugh and cringe."
    ),
    "fairy_tale": (
        "Write a fairy tale starting with 'Once upon a time...' set in the modern world. "
        "Blue ticks, voice notes, 'noob', Hinglish, late-night texts. "
        "Use their actual dynamic and real moments from the memories. "
        "Make the mundane feel magical — because in a way it is."
    ),
}

STYLE_QUERIES = {
    "romantic":    ["miss you love sweet caring tender", "late night deep honest conversation", "first wholesome moment together"],
    "poem":        ["banter tease playful joke daily", "sweet emotional caring moment", "hinglish funny natural conversation"],
    "bollywood":   ["dramatic emotional moment feeling", "argument sorry reconcile", "funny chaotic situation"],
    "roast_story": ["acha noob short reply teasing", "acting unbothered while caring", "pattern habit repeated behaviour"],
    "fairy_tale":  ["good morning routine daily ordinary", "wholesome unexpected sweet", "funny simple moment"],
}


async def generate_story(store: EmbeddingStore, style: str = "romantic") -> str:
    u1, u2 = settings.user1_name, settings.user2_name

    queries = STYLE_QUERIES.get(style, STYLE_QUERIES["romantic"])
    semantic = store.multi_query(queries, n_per_query=3)
    # Add random month samples for unexpected authentic detail
    spread   = store.month_spread(per_month=1)
    all_c    = semantic + spread
    random.shuffle(all_c)
    context  = build_context(all_c[:10])

    instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["romantic"]).format(u1=u1, u2=u2)

    user_content = f"""Real memories from {u1} and {u2}'s WhatsApp (with dates):

{context}

{instruction}

Ground rules:
- Only use details actually present in the memories above
- Reference specific dates when you mention events
- No AI phrases: "tapestry of emotions", "their bond", "journey together", "in conclusion"
- Start writing immediately — no preamble like "Here is your story:"
- Make it feel like it was written by someone who actually knows them"""

    return await call_llm([
        {"role": "system", "content": SYSTEM_PROMPT + f"\n\n{TONE_STORY}"},
        {"role": "user",   "content": user_content},
    ], temperature=1.05)
