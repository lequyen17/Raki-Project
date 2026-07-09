from datetime import datetime


from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

from app.models import (
    Conversation,
    ConversationParticipant,
    ConversationType,
    Message,
    MessageType,
)
from app.schemas.chat import (
    ConversationOut,
    MessageOut,
    ParticipantOut,
    UserBrief,
)
from app.services.user_client import fetch_users_by_ids


def _serialize_message(message: Message) -> MessageOut:
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        type=message.type.value,
        reply_to_message_id=message.reply_to_message_id,
        is_deleted=message.is_deleted,
        created_at=message.created_at,
    )


def _get_conversation_participants(
    db: Session, conversation_id: int
) -> list[ParticipantOut]:
    participants = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.left_at.is_(None),
        )
        .all()
    )
    users_map = fetch_users_by_ids([p.user_id for p in participants])
    print("participants:", [p.user_id for p in participants])
    print("users_map:", users_map)

    result = []

    for participant in participants:
        user = users_map.get(participant.user_id)

        result.append(
            ParticipantOut(
                user_id=participant.user_id,
                name=user.username,
                avatar=user.avatar if user else None,
                last_read_message_id=participant.last_read_message_id,
            )
        )

    return result


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


def list_conversations(db: Session, user_id: int) -> list[ConversationOut]:

    # 1. Subquery cực kỳ đơn giản: Chỉ lấy tin nhắn cuối của MỌI cuộc hội thoại
    # Không cần biết cuộc hội thoại đó của ai
    last_message_subquery = (
        db.query(Message)
        .distinct(Message.conversation_id)
        .order_by(Message.conversation_id, desc(Message.id))
        .subquery()
    )

    LastMessage = aliased(Message, last_message_subquery)

    # 2. Query chính: Bộ lọc user_id nằm ĐỘC NHẤT ở đây
    conversations = (
        db.query(Conversation, LastMessage)
        .join(
            ConversationParticipant,
            ConversationParticipant.conversation_id == Conversation.id,
        )
        # Khớp ID phòng chat của User với ID phòng chat của đống tin nhắn cuối kia
        .outerjoin(LastMessage, Conversation.id == LastMessage.conversation_id)
        .filter(
            ConversationParticipant.user_id == user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .order_by(desc(func.coalesce(LastMessage.id, 0)), desc(Conversation.id))
        .all()
    )

    results: list[ConversationOut] = []

    for conversation, last_message in conversations:

        results.append(
            ConversationOut(
                id=conversation.id,
                type=conversation.type.value,
                name=conversation.name,
                avatar=conversation.avatar,
                last_message_id=last_message.id if last_message else None,
                sender_id=last_message.sender_id if last_message else None,
                message_type=last_message.type.value if last_message else None,
                content=last_message.content if last_message else None,
                reply_to_message_id=(
                    last_message.reply_to_message_id if last_message else None
                ),
                is_deleted=last_message.is_deleted if last_message else None,
                message_created_at=last_message.created_at if last_message else None,
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

    other_users = fetch_users_by_ids([other_user_id])
    other_user = other_users.get(other_user_id)
    if not other_user:
        raise ValueError("OTHER_USER_NOT_FOUND")

    conversation = Conversation(
        type=ConversationType.PRIVATE,
        name=other_user.username,
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


def create_group_conversation(
    db: Session,
    creator_id: int,
    name: str,
    participant_ids: list[int],
) -> Conversation:
    unique_participants = {pid for pid in participant_ids if pid != creator_id}
    unique_participants.add(creator_id)

    if len(unique_participants) < 3:
        raise ValueError("GROUP_NEEDS_AT_LEAST_3_MEMBERS")

    conversation = Conversation(
        type=ConversationType.GROUP,
        name=name.strip(),
        created_by=creator_id,
    )
    db.add(conversation)
    db.flush()

    for participant_id in sorted(unique_participants):
        db.add(
            ConversationParticipant(
                conversation_id=conversation.id,
                user_id=participant_id,
                is_admin=(participant_id == creator_id),
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
) -> tuple[list[MessageOut], bool, list[ParticipantOut]]:
    if not user_is_participant(db, conversation_id, user_id):
        raise PermissionError("NOT_PARTICIPANT")

    query = db.query(Message).filter(
        Message.conversation_id == conversation_id,
    )

    if before_id:
        query = query.filter(Message.id < before_id)

    messages = query.order_by(desc(Message.id)).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()

    participants = _get_conversation_participants(db, conversation_id)

    return [_serialize_message(m) for m in messages], has_more, participants


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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if conversation:
        conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    return _serialize_message(message)


def mark_conversation_read(
    db: Session, conversation_id: int, user_id: int
) -> int | None:
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
        return last_message.id
    return None
