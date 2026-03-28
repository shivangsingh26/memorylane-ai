"""
Quiz mode — generates relationship trivia questions from chat history.
"""

import json
from embeddings import EmbeddingStore
from rag import SYSTEM_PROMPT, build_context
from llm import call_llm
from config import settings


async def generate_quiz(analytics: dict, store: EmbeddingStore) -> dict:
    u1, u2 = settings.user1_name, settings.user2_name

    # Pull diverse chunks for quiz material
    sample_chunks = store.sample_chunks(n=25)
    context = build_context(sample_chunks[:10])

    mc = analytics.get("message_count", {})
    init = analytics.get("initiations", {})
    emojis = list(analytics.get("top_emojis", {}).keys())[:3]

    user_content = f"""
You have access to {u1} and {u2}'s WhatsApp chat history. Use it to generate a fun relationship quiz.

Context from their chats:
{context}

Quick stats:
- {u1} sent {mc.get(u1, '?')} messages, {u2} sent {mc.get(u2, '?')} messages
- {u1} initiated {init.get(u1, '?')} conversations, {u2} initiated {init.get(u2, '?')}
- Top shared emojis: {' '.join(emojis) if emojis else 'unknown'}

Generate exactly 5 quiz questions in valid JSON format. The JSON must follow this exact structure:
{{
  "questions": [
    {{
      "question": "question text here",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "correct option text",
      "explanation": "fun explanation referencing a specific memory or stat"
    }}
  ]
}}

Question types to include (mix these):
1. "Who texts more / initiates more?" (use actual stats)
2. "Who said [specific phrase] first?" (from memories)
3. "What does [user] always say when [situation]?" (from memories)
4. "Which emoji does [user] use most?"
5. "What is their most common topic of conversation?"

Make questions specific, funny, and use actual content from the chat.
Return ONLY valid JSON — no markdown, no extra text.
""".strip()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_content},
    ]

    raw = await call_llm(messages)

    # Parse JSON from response
    try:
        # Strip potential markdown code fences
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Fallback: return raw in a wrapper
        return {"questions": [], "raw": raw, "error": "Could not parse JSON — see raw field"}
