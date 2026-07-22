## Getting started

```bash
git clone <your-repo-url>
cd ai-support-chatbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# then edit .env and add your ANTHROPIC_API_KEY (console.anthropic.com)

cd backend
uvicorn main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500` in a browser.

## Known limitations

- **Session storage is in-memory** (`_SESSIONS` dict in `chat_service.py`) — conversations are lost on server restart and won't scale across multiple worker processes. A production version would use Redis or a database instead.
- **Single business config per deployment** — swapping personas currently means changing `ACTIVE_BUSINESS_CONFIG` and restarting, not switching at request time.

