
from anthropic import Anthropic
from oauthlib.openid import connect

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

from retriever import search

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def build_system_prompt(retrieved_chunks: list[dict]) -> str:
    context_text = "\n\n".join(
        f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in retrieved_chunks
        )

    return f"""You are a customer support assistant for a dental clinic.

Answer the user's question using ONLY the information in the context below.
If the answer is not in the context, say you don't have that information
and suggest the user contact the clinic directly. Do not invent details.

Context:
{context_text}

Keep answers short and clear (2-4 sentences)."""



_SESSIONS: dict[str, list[dict]] = {}
MAX_HISTORY_MESSAGES = 20


def get_reply(session_id: str, user_message: str) -> str:
    history = _SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content":user_message})

    retrieved_chunks = search(user_message, n_results=3)
    system_prompt = build_system_prompt(retrieved_chunks)

    response = client.messages.create(
        model = ANTHROPIC_MODEL,
        max_tokens=500,
        system = system_prompt,
        messages= history,
    )

    reply_text = response.content[0].text
    history.append({"role": "assistant", "content": reply_text})

    if len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]

    return reply_text