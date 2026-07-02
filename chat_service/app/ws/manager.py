import json
import logging
from collections import defaultdict

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, dict[int, WebSocket]] = defaultdict(dict)

    async def connect(self, conversation_id: int, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[conversation_id][user_id] = websocket
        logger.info("WS connected: conversation=%s user=%s", conversation_id, user_id)

    def disconnect(self, conversation_id: int, user_id: int):
        self.active_connections[conversation_id].pop(user_id, None)
        if not self.active_connections[conversation_id]:
            self.active_connections.pop(conversation_id, None)
        logger.info("WS disconnected: conversation=%s user=%s", conversation_id, user_id)

    async def broadcast(self, conversation_id: int, payload: dict, exclude_user_id: int | None = None):
        connections = self.active_connections.get(conversation_id, {})
        message = json.dumps(payload, default=str)

        for user_id, websocket in list(connections.items()):
            if exclude_user_id and user_id == exclude_user_id:
                continue
            try:
                await websocket.send_text(message)
            except Exception as exc:
                logger.warning("WS send failed user=%s: %s", user_id, exc)
                self.disconnect(conversation_id, user_id)


manager = ConnectionManager()
