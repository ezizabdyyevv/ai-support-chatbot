from typing import Literal

from pydantic import BaseModel

class ChatRequest(BaseModel):
    session_id: str
    message: str
    language: Literal["en", "ru", "tr", "ka"] = "en"


class ChatResponse(BaseModel):
    reply: str
    session_id: str
