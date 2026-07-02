from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models import (
    Conversation,
    ConversationParticipant,
    ConversationType,
    Message,
    MessageRead,
    MessageType,
)
from app.schemas.chat import (
    ConversationOut,
    MessageOut,
    UserBrief,
)
from app.services.user_client import fetch_users_by_ids


def _participant_user_ids(conversation: Conversation, current_user_id: int) -> list[int]:
    return [
        p.user_id
        for p in conversation.participants
        if p.left_at is None and p.user_id != current_user_id
    ]


def _serialize_message(message: Message, users_map: dict[int, UserBrief]) -> MessageOut:
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        type=message.type.value,
        created_at=message.created_at,
        sender=users_map.get(message.sender_id),
    )


def _get_last_message(db: Session, conversation_id: int) -> Message | None:
    return (
        db.query(Message)
        .filter(
            Message.conversation_id == conversation_id,
            Message.is_deleted.is_(False),
        )
        .order_by(desc(Message.created_at))
        .first()
    )


def _unread_count(db: Session, conversation_id: int, user_id: int) -> int:
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .first()
    )
    if not participant:
        return 0

    query = db.query(func.count(Message.id)).filter(
        Message.conversation_id == conversation_id,
        Message.is_deleted.is_(False),
        Message.sender_id != user_id,
    )

    if participant.last_read_message_id:
        query = query.filter(Message.id > participant.last_read_message_id)

    return query.scalar() or 0


def list_conversations(db: Session, user_id: int) -> list[ConversationOut]:
    conversations = (
        db.query(Conversation)
        .join(ConversationParticipant)
        .filter(
            ConversationParticipant.user_id == user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .order_by(desc(Conversation.updated_at))
        .all()
    )

    other_user_ids: set[int] = set()
    sender_ids: set[int] = set()

    for conversation in conversations:
        other_user_ids.update(_participant_user_ids(conversation, user_id))
        last_message = _get_last_message(db, conversation.id)
        if last_message:
            sender_ids.add(last_message.sender_id)

    users_map = fetch_users_by_ids(list(other_user_ids | sender_ids))
    results: list[ConversationOut] = []

    for conversation in conversations:
        last_message = _get_last_message(db, conversation.id)
        other_ids = _participant_user_ids(conversation, user_id)
        other_user = users_map.get(other_ids[0]) if other_ids else None

        results.append(
            ConversationOut(
                id=conversation.id,
                type=conversation.type.value,
                name=conversation.name,
                created_at=conversation.created_at,
                updated_at=conversation.updated_at,
                other_user=other_user,
                last_message=(
                    _serialize_message(last_message, users_map)
                    if last_message
                    else None
                ),
                unread_count=_unread_count(db, conversation.id, user_id),
            )
        )

    return results


def get_or_create_private_conversation(
    db: Session, user_id: int, other_user_id: int
) -> Conversation:
    if user_id == other_user_id:
        raise ValueError("CANNOT_CHAT_WITH_SELF")

    existing = (
        db.query(Conversation)
        .join(ConversationParticipant)
        .filter(
            Conversation.type == ConversationType.PRIVATE,
            ConversationParticipant.user_id.in_([user_id, other_user_id]),
            ConversationParticipant.left_at.is_(None),
        )
        .group_by(Conversation.id)
        .having(func.count(ConversationParticipant.id) == 2)
        .first()
    )

    if existing:
        return existing

    conversation = Conversation(
        type=ConversationType.PRIVATE,
        created_by=user_id,
    )
    db.add(conversation)
    db.flush()

    for participant_id in (user_id, other_user_id):
        db.add(
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=participant_id,
            )
        )

    db.commit()
    db.refresh(conversation)
    return conversation


def user_is_participant(db: Session, conversation_id: int, user_id: int) -> bool:
    return (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .first()
        is not None
    )


def list_messages(
    db: Session,
    conversation_id: int,
    user_id: int,
    limit: int = 50,
    before_id: int | None = None,
) -> tuple[list[MessageOut], bool]:
    if not user_is_participant(db, conversation_id, user_id):
        raise PermissionError("NOT_PARTICIPANT")

    query = db.query(Message).filter(
        Message.conversation_id == conversation_id,
        Message.is_deleted.is_(False),
    )

    if before_id:
        query = query.filter(Message.id < before_id)

    messages = query.order_by(desc(Message.id)).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()

    sender_ids = {m.sender_id for m in messages}
    users_map = fetch_users_by_ids(list(sender_ids))

    return [_serialize_message(m, users_map) for m in messages], has_more


def create_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str,
) -> MessageOut:
    if not user_is_participant(db, conversation_id, sender_id):
        raise PermissionError("NOT_PARTICIPANT")

    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content.strip(),
        type=MessageType.TEXT,
    )
    db.add(message)

    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation:
        conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    users_map = fetch_users_by_ids([sender_id])
    return _serialize_message(message, users_map)


def mark_conversation_read(db: Session, conversation_id: int, user_id: int) -> None:
    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .first()
    )
    if not participant:
        raise PermissionError("NOT_PARTICIPANT")

    last_message = _get_last_message(db, conversation_id)
    if last_message:
        participant.last_read_message_id = last_message.id
        db.commit()
