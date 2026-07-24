from fastapi import FastAPI
from models import ChatRequest, ChatResponse
from chat_service import get_reply
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()

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
def chat(request: ChatRequest) -> ChatResponse:
    reply_text = get_reply(request.session_id, request.message)
    return ChatResponse(reply=reply_text, session_id=request.session_id)




if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
