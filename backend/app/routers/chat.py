from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import uuid

from app.models.user import User
from app.models.chat import ChatSession
from app.schemas.chat import ChatMessageCreate, ChatSessionResponse, ChatHistoryResponse
from app.auth.deps import get_current_active_user
from app.llm.chat_engine import chat_engine

router = APIRouter()

@router.post("/message")
async def send_message(
    chat_req: ChatMessageCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a message to the AI Chatbot and get a streaming response.
    If session_id is empty, a new session is created.
    """
    session_id = chat_req.session_id
    
    if not session_id:
        # Create a new session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            user_id=str(current_user.id),
            session_id=session_id
        )
        await chat_session.insert()
    else:
        # Retrieve existing session
        chat_session = await ChatSession.find_one(
            {"session_id": session_id, "user_id": str(current_user.id)}
        )
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
            
    # Return streaming response
    return await chat_engine.get_streaming_response(chat_req.message, chat_session)


@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_user_sessions(current_user: User = Depends(get_current_active_user)):
    """Get all chat sessions for the current user."""
    sessions = await ChatSession.find({"user_id": str(current_user.id)}).sort("-updated_at").to_list()
    return sessions


@router.get("/history/{session_id}", response_model=ChatHistoryResponse)
async def get_session_history(
    session_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get full message history for a specific session."""
    chat_session = await ChatSession.find_one(
        {"session_id": session_id, "user_id": str(current_user.id)}
    )
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    return chat_session
