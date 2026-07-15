from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    BigInteger,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base import Base


class ConversationType(str, enum.Enum):
    PRIVATE = "private"
    GROUP = "group"


class MessageType(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    FILE = "file"
    STICKER = "sticker"
    SYSTEM = "system"


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=True)
    avatar = Column(String, nullable=True)

    type = Column(Enum(ConversationType), default=ConversationType.PRIVATE)

    created_by = Column(BigInteger)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    participants = relationship(
        "ConversationParticipant", back_populates="conversation"
    )
    messages = relationship("Message", back_populates="conversation")

    def __repr__(self):
        return f"{self.type} - {self.id}"


class ConversationParticipant(Base):
    __tablename__ = "conversation_participant"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(Integer, ForeignKey("conversation.id", ondelete="CASCADE"))
    user_id = Column(BigInteger)

    joined_at = Column(DateTime, default=datetime.utcnow)
    left_at = Column(DateTime, nullable=True)

    is_admin = Column(Boolean, default=False)

    last_read_message_id = Column(
        Integer, ForeignKey("message.id", use_alter=True), nullable=True
    )

    # relationships
    conversation = relationship("Conversation", back_populates="participants")
    last_read_message = relationship("Message", foreign_keys=[last_read_message_id])

    __table_args__ = (Index("idx_conversation_participant_user_id", "user_id"),)

    def __repr__(self):
        return f"Conversation {self.conversation_id} - User {self.user_id}"


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, primary_key=True, index=True)

    conversation_id = Column(Integer, ForeignKey("conversation.id", ondelete="CASCADE"))
    sender_id = Column(BigInteger)

    type = Column(Enum(MessageType), default=MessageType.TEXT)

    content = Column(Text, nullable=True)

    reply_to_message_id = Column(Integer, ForeignKey("message.id"), nullable=True)

    is_deleted = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    conversation = relationship("Conversation", back_populates="messages")

    reply_to_message = relationship("Message", remote_side=[id])

    attachments = relationship("Attachment", back_populates="message")

    __table_args__ = (
        Index("idx_message_conversation_created_at", "conversation_id", "created_at"),
    )

    def __repr__(self):
        return f"Message {self.id}"


class Attachment(Base):
    __tablename__ = "attachment"

    id = Column(Integer, primary_key=True, index=True)

    message_id = Column(Integer, ForeignKey("message.id", ondelete="CASCADE"))

    file_name = Column(String(255))
    file_url = Column(String)
    mime_type = Column(String(100))
    size = Column(BigInteger)

    message = relationship("Message", back_populates="attachments")

    def __repr__(self):
        return self.file_name
