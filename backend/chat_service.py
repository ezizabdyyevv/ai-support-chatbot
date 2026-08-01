
from anthropic import Anthropic

from pathlib import  Path

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

from retriever import search
import json

import threading

client = Anthropic(api_key=ANTHROPIC_API_KEY)

PERSONA_CONFIG_PATH = Path(__file__).parent.parent / "persona.json"
with open(PERSONA_CONFIG_PATH, encoding="utf-8") as f:
    persona = json.load(f)


CONFIDENCE_THRESHOLD = 1.2

def translate_to_english(text: str, language: str) -> str:
    if language == "en":
        return text

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=200,
        system="Translate the user's message to English. Reply with ONLY the translation, nothing else.",
        messages=[{"role": "user", "content": text}],
    )
    return "".join(block.text for block in response.content if block.type == "text")

LANGUAGE_NAMES = {
    "en": "English",
    "ru": "Russian",
    "tr": "Turkish",
    "ka": "Georgian",
}


def build_system_prompt(retrieved_chunks: list[dict], language: str = "en") -> str:
    relevant_chunks = [c for c in retrieved_chunks if c["distance"] <= CONFIDENCE_THRESHOLD]
    language_name = LANGUAGE_NAMES.get(language, "English")

    identity = f"""You are {persona['name']}, a customer support assistant for {persona['business_name']}.
Tone: {persona['tone']}
Always reply in {language_name}, even though the context below is in English."""

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

_session_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _get_session_lock(session_id: str) -> threading.Lock:
    with _locks_guard:
        if session_id not in _session_locks:
            _session_locks[session_id] = threading.Lock()
        return _session_locks[session_id]



def get_reply(session_id: str, user_message: str, language: str = "en") -> str:
    lock = _get_session_lock(session_id)
    with lock:
        history = _SESSIONS.setdefault(session_id, [])
        history.append({"role": "user", "content": user_message})

        search_query = translate_to_english(user_message, language)
        retrieved_chunks = search(search_query, n_results=3)
        relevant_chunks = retrieved_chunks  # confidence filtreleme build_system_prompt içinde
        system_prompt = build_system_prompt(retrieved_chunks, language)

        response = client.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=500,
            system=system_prompt,
            messages=history,
        )

        reply_text = "".join(block.text for block in response.content if block.type == "text")
        history.append({"role": "assistant", "content": reply_text})

        if len(history) > MAX_HISTORY_MESSAGES:
            del history[:-MAX_HISTORY_MESSAGES]

        return reply_text