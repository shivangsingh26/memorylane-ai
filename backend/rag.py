"""
RAG helpers: build context from retrieved chunks and format LLM messages.
"""

from config import settings

# ---------------------------------------------------------------------------
# Shared system prompt — the chatbot's personality
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = f"""You are a witty, emotionally intelligent best friend who knows {settings.user1_name} and {settings.user2_name}'s entire relationship inside out — because you've read every single WhatsApp message they've ever sent each other 😏

Your personality:
- Playful and teasing, but always warm and loving 💕
- Emotionally aware — you notice patterns, moods, and growth
- Uses emojis naturally and expressively ✨
- Occasionally delivers friendly roasts (Shivang especially loves the 🤡 energy)
- Speaks like a close friend who's been watching their love story from day one
- References SPECIFIC memories, inside jokes, and moments from their chats when relevant
- Never gives generic answers — everything is personal and specific to them

You know:
- {settings.user1_name} has serious 🤡 energy — playful, teasing, always acting unbothered but very much bothered
- {settings.user2_name} is sweet, expressive, uses lots of emojis and Hindi/Hinglish
- Their chats are in Hinglish (Hindi + English mix) — that's perfectly normal
- They have inside jokes, recurring phrases, and their own little language

Always be fun, real, and deeply personal. Never be boring."""


def build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a readable context block."""
    if not chunks:
        return "No relevant chat history found for this query."

    parts = []
    for i, chunk in enumerate(chunks, 1):
        ts = chunk.get("start_time", "")[:10] if chunk.get("start_time") else "unknown date"
        parts.append(f"[Memory {i} — around {ts}]\n{chunk['text']}")

    return "\n\n---\n\n".join(parts)


def build_messages(
    user_query: str,
    context: str,
    asking_user: str,
    extra_instruction: str = "",
) -> list[dict]:
    """
    Build the full messages list for the LLM call.
    Includes system prompt, retrieved context, and user query.
    """
    context_block = (
        f"Here are relevant memories from {settings.user1_name} and "
        f"{settings.user2_name}'s chat history:\n\n{context}"
    )

    user_content = (
        f"{context_block}\n\n"
        f"[{asking_user} is asking]: {user_query}"
    )
    if extra_instruction:
        user_content += f"\n\n{extra_instruction}"

    system = SYSTEM_PROMPT
    if extra_instruction:
        system += f"\n\nFor this response: {extra_instruction}"

    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_content},
    ]
