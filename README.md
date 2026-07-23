# AI Customer Support Chatbot (RAG-powered)

A customer-support chatbot backend for a dental clinic, built with FastAPI, ChromaDB, and the Claude API. Instead of hard-coding business information into a single prompt, the bot retrieves the most relevant passages from a document collection for each question — a full Retrieval-Augmented Generation (RAG) pipeline.

## Evolution note

This project started as a simpler bot with a single hard-coded JSON config (`business_configs/*.json`) driving the system prompt — see commit history. That approach breaks down once a business's knowledge base grows past a single FAQ page: you can't fit an entire policy manual into a prompt. This version replaces the static config with a proper retrieval pipeline: documents are chunked, embedded, and stored in a vector database, and only the passages relevant to *this specific question* are retrieved and passed to the model.

## How it works

**Indexing (offline, run once via `build_index.py`):**
1. Every `.txt` file in `documents/` is split into paragraph-level chunks
2. Each chunk is embedded and stored in a persistent ChromaDB collection

**Query (runtime, every request):**
1. Client sends `{session_id, message}` to `POST /api/chat`
2. `retriever.py` embeds the question and finds the 3 most similar chunks in ChromaDB
3. `chat_service.py` builds a system prompt containing only those chunks, explicitly instructing the model not to answer beyond what's given
4. The full conversation history (for that session) plus the fresh system prompt is sent to Claude
5. The reply is returned and appended to session history

## Tech stack

- **Backend:** FastAPI + Uvicorn
- **Vector database:** ChromaDB (persistent, local, built-in embedding function — no external embedding API needed)
- **LLM:** Claude API (`anthropic` SDK)
- **Frontend:** Vanilla HTML/CSS/JS, no build step

## Project structure


ai-support-chatbot/
├── backend/
│ ├── main.py # FastAPI routes, CORS
│ ├── chat_service.py # Session memory, RAG-based system prompt, Claude API calls
│ ├── retriever.py # Embeds a query and searches ChromaDB
│ ├── build_index.py # One-time script: chunks documents/, builds the ChromaDB index
│ ├── models.py # Request/response schemas
│ └── config.py # Reads API key + model name from .env
├── documents/ # Source knowledge base (plain text files)
├── chroma_db/ # Generated vector index (gitignored, rebuilt via build_index.py)
├── frontend/
│ └── index.html
├── requirements.txt
└── .env.example

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
python build_index.py       # builds the vector index from documents/
uvicorn main:app --reload --port 8000
```

In a second terminal:

```bash
cd frontend
python3 -m http.server 5500
```

Open `http://localhost:5500`.

## Known limitations

- **Session storage is in-memory** — conversations are lost on server restart.
- **Chunking is paragraph-based** (splitting on blank lines) — works well for these structured documents, but a production system would likely use a more robust, size-aware chunking strategy for arbitrary documents.
- **No re-ranking step** — the top-3 chunks from vector similarity are used as-is. For a larger document collection, a re-ranking model would likely improve precision.
- **Single fixed business identity** — the earlier config-driven persona (business name, tone, hours) was removed when the JSON config was replaced by the document-based knowledge base. A production version would keep a small identity/tone config alongside the document-based knowledge base, rather than hard-coding it into the prompt.

## What I'd add next

- Re-introduce a lightweight persona config (name, tone) that combines with retrieved context, so the identity layer and the knowledge layer are decoupled again
- Add a "confidence" check — if retrieved chunks have low similarity scores, have the bot proactively say it's unsure rather than answering from weak matches
- Move ChromaDB to a client-server deployment (rather than local persistent file) for multi-instance scaling