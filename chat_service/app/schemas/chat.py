from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserBrief(BaseModel):
    id: int
    username: str
    first_name: str = ""
    last_name: str = ""
    avatar: str | None = None


class ConversationCreate(BaseModel):
    other_user_id: int


class GroupConversationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    participant_ids: list[int] = Field(default_factory=list)


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    reply_to_message_id: Optional[int] = None


class MessageOut(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    content: Optional[str]
    type: str
    reply_to_message_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ParticipantOut(BaseModel):
    user_id: int
    name: str
    avatar: Optional[str] = None
    last_read_message_id: Optional[int] = None
    joined_at: Optional[datetime] = None
    is_admin: bool = False


class ConversationOut(BaseModel):
    id: int
    type: str
    name: Optional[str]
    avatar: Optional[str]

    last_message_id: Optional[int] = None
    sender_id: Optional[int] = None
    message_type: Optional[str] = None
    content: Optional[str] = None
    reply_to_message_id: Optional[int] = None
    is_deleted: Optional[bool] = None
    message_created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ConversationListResponse(BaseModel):
    results: list[ConversationOut]


class MessageListResponse(BaseModel):
    results: list[MessageOut]
    has_more: bool = False
    participants: list[ParticipantOut] = Field(default_factory=list)


class ConversationDetailOut(BaseModel):
    id: int
    type: str
    name: Optional[str]
    avatar: Optional[str]
    created_at: datetime
    created_by: int
    created_by_name: str
    participants: list[ParticipantOut] = Field(default_factory=list)


class ConversationUpdateName(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)


class MembersAddBody(BaseModel):
    participant_ids: list[int] = Field(default_factory=list)


class MemberAdminUpdateBody(BaseModel):
    is_admin: bool = False


class ReadConversationResponse(BaseModel):
    success: bool
    conversation_id: int
    last_read_message_id: Optional[int] = None
    seen_by_ids: list[int] = Field(default_factory=list)
