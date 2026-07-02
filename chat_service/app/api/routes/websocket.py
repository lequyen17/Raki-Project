import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import get_user_id_from_token
from app.db.session import SessionLocal
from app.services import chat_service
from app.ws.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(...),
):
    try:
        user_id = get_user_id_from_token(token)
    except Exception:
        await websocket.close(code=4001)
        return

    db: Session = SessionLocal()
    try:
        if not chat_service.user_is_participant(db, conversation_id, user_id):
            await websocket.close(code=4003)
            return
    finally:
        db.close()

    await manager.connect(conversation_id, user_id, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            content = (data.get("content") or "").strip()
            if not content:
                continue

            db = SessionLocal()
            try:
                message = chat_service.create_message(
                    db, conversation_id, user_id, content
                )
                chat_service.mark_conversation_read(db, conversation_id, user_id)
            finally:
                db.close()

            await manager.broadcast(
                conversation_id,
                {"type": "message", "data": message.model_dump()},
            )
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, user_id)
    except Exception as exc:
        logger.error("WebSocket error: %s", exc)
        manager.disconnect(conversation_id, user_id)
