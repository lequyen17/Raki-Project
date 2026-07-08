from datetime import datetime


from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from sqlalchemy.orm import aliased

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


def _participant_user_ids(
    conversation: Conversation, current_user_id: int
) -> list[int]:
    return [
        p.user_id
        for p in conversation.participants
        if p.left_at is None and p.user_id != current_user_id
    ]


def _serialize_message(message: Message, users_map: dict[int, UserBrief]) -> MessageOut:
    seen_by_ids = [
        read.user_id for read in message.reads if read.user_id != message.sender_id
    ]
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        type=message.type.value,
        created_at=message.created_at,
        sender=users_map.get(message.sender_id),
        seen_by_ids=seen_by_ids,
        seen_count=len(seen_by_ids),
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

    # other_user = db.query(User).filter(User.id == other_user_id).first()
    # if not other_user:
    #     raise ValueError("OTHER_USER_NOT_FOUND")

    # # Lấy tên đối phương (bạn thay .full_name hoặc .username tùy theo bảng User của bạn nhé)
    # other_user_name = other_user.username

    conversation = Conversation(
        type=ConversationType.PRIVATE,
        name="default",
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
    message_ids = [m.id for m in messages]
    if message_ids:
        reads = (
            db.query(MessageRead).filter(MessageRead.message_id.in_(message_ids)).all()
        )
        reads_by_message: dict[int, list[MessageRead]] = {}
        for read in reads:
            reads_by_message.setdefault(read.message_id, []).append(read)
        for message in messages:
            message.reads = reads_by_message.get(message.id, [])

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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if conversation:
        conversation.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(message)

    message.reads = []
    users_map = fetch_users_by_ids([sender_id])
    return _serialize_message(message, users_map)


def get_message_seen_by_ids(db: Session, message_id: int, sender_id: int) -> list[int]:
    reads = (
        db.query(MessageRead)
        .filter(
            MessageRead.message_id == message_id,
            MessageRead.user_id != sender_id,
        )
        .all()
    )
    return [read.user_id for read in reads]


def mark_conversation_read(
    db: Session, conversation_id: int, user_id: int
) -> tuple[int | None, list[int]]:
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
        read = (
            db.query(MessageRead)
            .filter(
                MessageRead.message_id == last_message.id,
                MessageRead.user_id == user_id,
            )
            .first()
        )
        if not read:
            db.add(MessageRead(message_id=last_message.id, user_id=user_id))
        db.commit()
        seen_by_ids = get_message_seen_by_ids(
            db, last_message.id, last_message.sender_id
        )
        return last_message.id, seen_by_ids
    return None, []
