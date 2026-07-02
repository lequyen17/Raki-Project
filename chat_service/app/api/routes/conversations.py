from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.security import get_current_user_id
from app.schemas.chat import (
    ConversationCreate,
    ConversationListResponse,
    ConversationOut,
    MessageCreate,
    MessageListResponse,
    MessageOut,
)
from app.services import chat_service
from app.services.user_client import fetch_users_by_ids

router = APIRouter(prefix="/conversations", tags=["Conversations"])


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    results = chat_service.list_conversations(db, user_id)
    return {"results": results}


@router.post("", response_model=ConversationOut)
def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        conversation = chat_service.get_or_create_private_conversation(
            db, user_id, body.other_user_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    users_map = fetch_users_by_ids([body.other_user_id])
    other_user = users_map.get(body.other_user_id)

    return ConversationOut(
        id=conversation.id,
        type=conversation.type.value,
        name=conversation.name,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        other_user=other_user,
        last_message=None,
        unread_count=0,
    )


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
def get_messages(
    conversation_id: int,
    before_id: int | None = Query(None),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        results, has_more = chat_service.list_messages(
            db, conversation_id, user_id, limit=limit, before_id=before_id
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")

    return {"results": results, "has_more": has_more}


@router.post("/{conversation_id}/messages", response_model=MessageOut)
def send_message(
    conversation_id: int,
    body: MessageCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return chat_service.create_message(
            db, conversation_id, user_id, body.content
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")


@router.post("/{conversation_id}/read")
def mark_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        chat_service.mark_conversation_read(db, conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    return {"success": True}
