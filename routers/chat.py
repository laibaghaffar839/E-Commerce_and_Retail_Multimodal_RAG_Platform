from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from db.database import get_db
from db.models import ChatRoom, ChatMessage, User
from services.auth import get_current_user

from schemas.chat import ChatRequest, ChatResponse
from services.rag import generate_answer

router = APIRouter(prefix="/chat",tags=["Chat"])

# POST /chat/{room_id}
# Ask a question in a chat room
@router.post("/{room_id}",response_model=ChatResponse)
def chat(
    room_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check that the room belongs to the logged-in user
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()
    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )

    # 2. Get last 6 messages from conversation history
    history_rows = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.room_id == room_id
        )
        .order_by(
            ChatMessage.created_at.desc()
        )
        .limit(6)
        .all()
    )
    # Reverse so oldest message comes first
    history_rows.reverse()

    # 3. Convert database messages into Groq message format
    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in history_rows
    ]
    # 4. Generate RAG answer
    result = generate_answer(
        query=request.query,
        room_id=room_id,
        history=history
    )
    # 5. Save user's question
    user_message = ChatMessage(
        room_id=room_id,
        user_id=current_user.id,
        role="user",
        content=request.query,
        sources=None
    )
    db.add(user_message)
    # 6. Save assistant's answer
    assistant_message = ChatMessage(
        room_id=room_id,
        user_id=current_user.id,
        role="assistant",
        content=result["answer"],
        sources=result["sources"]
    )
    db.add(assistant_message)

    # 7. Commit both messages
    db.commit()
    # 8. Return answer and sources
    return {
        "answer": result["answer"],
        "sources": result["sources"]
    }

# GET /chat/{room_id}/history
# Get chat history
@router.get("/{room_id}/history")
def get_chat_history(
    room_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check room ownership
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )


    # 2. Get messages
    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.room_id == room_id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


    # 3. Return history
    return messages

# DELETE /chat/{room_id}/history
# Clear chat history

@router.delete("/{room_id}/history")
def delete_chat_history(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # 1. Check room ownership
    room = db.query(ChatRoom).filter(
        ChatRoom.id == room_id,
        ChatRoom.owner_id == current_user.id
    ).first()

    if room is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Room not found or you don't have permission"
        )


    # 2. Delete all messages from the room
    db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id
    ).delete(
        synchronize_session=False
    )


    # 3. Save changes
    db.commit()


    # 4. Return success message
    return {
        "message": "Chat history deleted successfully"
    }