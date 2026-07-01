from app.db.base import Base
from app.db.session import engine  # hoặc nơi bạn tạo engine

# IMPORT ALL MODELS (rất quan trọng)
from app.models.model import (
    Conversation,
    ConversationParticipant,
    Message,
    Attachment,
    MessageRead,
)


def init_db():
    # tạo toàn bộ bảng
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
