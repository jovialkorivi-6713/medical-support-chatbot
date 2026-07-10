from beanie import Document
from pydantic import Field
from typing import List, Dict, Any
from datetime import datetime

class ChatSession(Document):
    user_id: str
    session_id: str
    title: str = "New Conversation"
    messages: List[Dict[str, Any]] = []  # Store LangChain message dicts
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "chat_sessions"
