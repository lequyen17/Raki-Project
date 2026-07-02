from app.db.base import Base
from app.db.session import engine

from app.models import (  # noqa: F401
    Attachment,
    Conversation,
    ConversationParticipant,
    Message,
    MessageRead,
)


def init_db():
    Base.metadata.create_all(bind=engine)
