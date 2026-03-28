"""
Story / Poem generator — creates a creative piece about the couple from their chats.
"""

from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, build_context
from llm import call_llm
from config import settings

STYLE_PROMPTS = {
    "romantic": "Write a beautiful, heartfelt short story (300-400 words) about their love story.",
    "poem": "Write a playful, witty poem (12-16 lines) about their relationship. Mix English and Hinglish naturally.",
    "bollywood": "Write a dramatic Bollywood-style narrative about their love story. Be over-the-top, filmy, and hilarious. Use dramatic Bollywood tropes.",
    "roast_story": "Write a funny 'how they actually met and texted' story that gently roasts both of them throughout.",
    "fairy_tale": "Write a fairy tale beginning with 'Once upon a time...' but set in the modern world with WhatsApp, memes, and Hinglish.",
}


async def generate_story(store: EmbeddingStore, style: str = "romantic") -> str:
    u1, u2 = settings.user1_name, settings.user2_name

    sample_chunks = store.sample_chunks(n=15)
    context = build_context(sample_chunks[:8])

    style_instruction = STYLE_PROMPTS.get(style, STYLE_PROMPTS["romantic"])

    user_content = f"""
Here are memories from {u1} and {u2}'s WhatsApp chat history:

{context}

{style_instruction}

Important rules:
- Use SPECIFIC details, quotes, and moments from the chat history above
- Reference their actual personalities: {u1} with his 🤡 energy, {u2} being sweet and expressive
- Make it feel REAL and personal — not generic
- Use emojis naturally
- Write something they'd both smile (and cringe) at

Begin the story/poem now:
""".strip()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    return await call_llm(messages)
