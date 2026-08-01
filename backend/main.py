
from models import ChatRequest, ChatResponse
from chat_service import get_reply
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles


from fastapi import FastAPI, Request, HTTPException

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health():
    return{"status": {"ok"}}


@app.post("/api/chat")
@limiter.limit("10/minute")
def chat(request: Request, chat_request: ChatRequest) -> ChatResponse:
    if not chat_request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    reply_text = get_reply(chat_request.session_id, chat_request.message, chat_request.language)
    return ChatResponse(reply=reply_text, session_id=chat_request.session_id)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
