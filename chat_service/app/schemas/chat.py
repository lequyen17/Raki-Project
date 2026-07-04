from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBrief(BaseModel):
    id: int
    username: str
    first_name: str = ""
    last_name: str = ""


class ConversationCreate(BaseModel):
    other_user_id: int


class GroupConversationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    participant_ids: list[int] = Field(default_factory=list)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: Optional[str]
    type: str
    created_at: datetime
    sender: Optional[UserBrief] = None
    seen_by_ids: list[int] = Field(default_factory=list)
    seen_count: int = 0

    class Config:
        from_attributes = True


class ConversationOut(BaseModel):
    id: int
    type: str
    name: Optional[str]
    created_at: datetime
    updated_at: datetime
    other_user: Optional[UserBrief] = None
    participants: list[UserBrief] = Field(default_factory=list)
    last_message: Optional[MessageOut] = None
    unread_count: int = 0

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    results: list[ConversationOut]


class MessageListResponse(BaseModel):
    results: list[MessageOut]
    has_more: bool = False


class ReadConversationResponse(BaseModel):
    success: bool
    conversation_id: int
    last_read_message_id: Optional[int] = None
    seen_by_ids: list[int] = Field(default_factory=list)
