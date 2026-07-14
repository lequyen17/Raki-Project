import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.security import get_user_id_from_token
from app.db.session import SessionLocal
from app.services import chat_service
from app.ws.manager import manager

logger = logging.getLogger(__name__)
router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    # 1. Chấp nhận kết nối và ghi tên vào "sổ hộ khẩu"
    await manager.connect(user_id, websocket)

    try:
        while True:
            # Giữ cho đường ống luôn mở và lắng nghe nếu client gửi gì đó lên qua WS
            # (Nếu bạn chỉ dùng WS để nhận tin nhắn từ server, dòng này chỉ để giữ kết nối)
            data = await websocket.receive_text()

    except WebSocketDisconnect:
        # 2. Nếu user tắt trình duyệt hoặc mất mạng, xóa họ khỏi "sổ hộ khẩu"
        manager.disconnect(user_id)
