
from anthropic import Anthropic

from pathlib import  Path

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

from retriever import search
import json

client = Anthropic(api_key=ANTHROPIC_API_KEY)

PERSONA_CONFIG_PATH = Path(__file__).parent.parent / "persona.json"
with open(PERSONA_CONFIG_PATH, encoding="utf-8") as f:
    persona = json.load(f)


CONFIDENCE_THRESHOLD = 1.2


def build_system_prompt(retrieved_chunks: list[dict]) -> str:
    relevant_chunks = [c for c in retrieved_chunks if c["distance"] <= CONFIDENCE_THRESHOLD]

    identity = f"""You are {persona['name']}, a customer support assistant for {persona['business_name']}.
Tone: {persona['tone']}"""

    if not relevant_chunks:
        return f"""{identity}

The user's question does not match anything in your knowledge base.
Tell them you don't have that information and suggest they contact the
clinic directly. Do not attempt to answer from general knowledge."""

    context_text = "\n\n".join(
        f"[Source: {chunk['source']}]\n{chunk['text']}" for chunk in relevant_chunks
    )

    return f"""{identity}

Answer the user's question using ONLY the information in the context below.
If the answer is not fully in the context, say you don't have that information
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

    reply_text = "".join(block.text for block in response.content if block.type == "text")
    history.append({"role": "assistant", "content": reply_text})

    if len(history) > MAX_HISTORY_MESSAGES:
        del history[:-MAX_HISTORY_MESSAGES]

    return reply_text