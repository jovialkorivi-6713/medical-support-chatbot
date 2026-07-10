from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class ChatMessageCreate(BaseModel):
    session_id: str
    message: str

class ChatSessionResponse(BaseModel):
    id: str
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
