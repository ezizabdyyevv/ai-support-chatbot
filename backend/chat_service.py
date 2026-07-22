import json
from pathlib import Path

from anthropic import Anthropic
from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL

client = Anthropic(api_key=ANTHROPIC_API_KEY)

BUSINESS_CONFIG_PATH = Path(__file__).parent.parent / "business_configs" / "dental_clinic.json"
with open(BUSINESS_CONFIG_PATH, encoding="utf-8") as f:
    business = json.load(f)


def build_system_prompt(business: dict) -> str:
    services_text = "\n".join(f"- {s['name']}: {s['price_note']}" for s in business["services"])
    hours_text = "\n".join(f"- {day}: {hrs}" for day, hrs in business["hours"].items())
    faq_text = "\n".join(f"S: {item['question']}\nC: {item['answer']}" for item in business["faq"])

    return f"""Sen {business['business_name']} adlı işletmenin müşteri destek asistanısın.

İşletme: {business['description']}

Hizmetler:
{services_text}

Çalışma saatleri:
{hours_text}

Sık sorulan sorular:
{faq_text}

Ton: {business['tone']}
Kural: {business['escalation_note']}
Kısa ve net cevap ver (2-4 cümle)."""


SYSTEM_PROMPT = build_system_prompt(business)

_SESSIONS: dict[str, list[dict]] = {}


def get_reply(session_id: str, user_message: str) -> str:
    history = _SESSIONS.setdefault(session_id, [])
    history.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=500,
        system=SYSTEM_PROMPT,
        messages=history,
    )

    reply_text = response.content[0].text
    history.append({"role": "assistant", "content": reply_text})

    return reply_text