from pydantic import BaseModel
from typing import Optional, List

class Chat(BaseModel):
    role: str
    message: str

class ChatPayload(BaseModel):
    title: str
    message: str


class CreateRoomPayload(BaseModel):
    title: str


class RenamePayload(BaseModel):
    old_title: str
    new_title: str

class ScrapeRequest(BaseModel):
    url: str

class QueryRequest(BaseModel):
    question: str
    top_k: int = 3

class ChatRequest(BaseModel):
    session_id: str
    message: str

class AskRequest(BaseModel):
    question: str
    top_k: Optional[int] = 3
    title: Optional[str] = None
