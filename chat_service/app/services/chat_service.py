from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import desc, func
from sqlalchemy.orm import Session, aliased, joinedload

from app.models import (
    Attachment,
    Conversation,
    ConversationParticipant,
    ConversationType,
    Message,
    MessageType,
)
from app.schemas.chat import (
    AttachmentOut,
    ConversationOut,
    MessageOut,
    ParticipantOut,
)
from app.services.user_client import fetch_users_by_ids


def _mime_to_message_type(mime_type: str | None) -> MessageType:
    mime = (mime_type or "").lower()
    if mime.startswith("image/"):
        return MessageType.IMAGE
    if mime.startswith("video/"):
        return MessageType.VIDEO
    if mime.startswith("audio/"):
        return MessageType.AUDIO
    return MessageType.FILE


def _resolve_message_type(
    content: str | None,
    attachment_mime_types: Sequence[str | None],
) -> MessageType:
    if not attachment_mime_types:
        return MessageType.TEXT

    types = {_mime_to_message_type(m) for m in attachment_mime_types}
    if len(types) == 1:
        return next(iter(types))
    # Nhiều loại file khác nhau trong cùng một tin nhắn -> FILE
    return MessageType.FILE


def _serialize_attachment(attachment: Attachment) -> AttachmentOut:
    return AttachmentOut(
        id=attachment.id,
        file_name=attachment.file_name,
        file_url=attachment.file_url,
        mime_type=attachment.mime_type,
        size=attachment.size,
    )


def _serialize_message(message: Message) -> MessageOut:
    attachments = [_serialize_attachment(a) for a in (message.attachments or [])]
    return MessageOut(
        id=message.id,
        conversation_id=message.conversation_id,
        sender_id=message.sender_id,
        content=message.content,
        type=message.type.value,
        reply_to_message_id=message.reply_to_message_id,
        is_deleted=message.is_deleted,
        created_at=(
            message.created_at.replace(tzinfo=timezone.utc)
            if message.created_at
            else None
        ),
        attachments=attachments,
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

    result = []

    for participant in participants:
        user = users_map.get(participant.user_id)

        result.append(
            ParticipantOut(
                user_id=participant.user_id,
                name=user.username if user else f"user_{participant.user_id}",
                avatar=user.avatar if user else None,
                last_read_message_id=participant.last_read_message_id,
                joined_at=(
                    participant.joined_at.replace(tzinfo=timezone.utc)
                    if participant.joined_at
                    else None
                ),
                is_admin=participant.is_admin,
            )
        )

    return result


def get_conversation_detail(db: Session, conversation_id: int, user_id: int) -> dict:
    if not user_is_participant(db, conversation_id, user_id):
        raise PermissionError("NOT_PARTICIPANT")

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise ValueError("CONVERSATION_NOT_FOUND")

    participants = _get_conversation_participants(db, conversation_id)
    creator_map = fetch_users_by_ids([conversation.created_by])
    creator = creator_map.get(conversation.created_by)
    creator_name = creator.username if creator else f"user_{conversation.created_by}"

    avatar = conversation.avatar
    if not avatar and conversation.type == ConversationType.PRIVATE:
        other = next((p for p in participants if p.user_id != user_id), None)
        avatar = other.avatar if other else None

    return {
        "id": conversation.id,
        "type": conversation.type.value,
        "name": conversation.name,
        "avatar": avatar,
        "created_at": (
            conversation.created_at.replace(tzinfo=timezone.utc)
            if conversation.created_at
            else None
        ),
        "created_by": conversation.created_by,
        "created_by_name": creator_name,
        "participants": participants,
    }


def update_group_name(
    db: Session,
    conversation_id: int,
    user_id: int,
    name: str,
) -> Conversation:
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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise ValueError("CONVERSATION_NOT_FOUND")

    conversation.name = name.strip()
    db.commit()
    db.refresh(conversation)
    return conversation


def update_conversation_avatar(
    db: Session,
    conversation_id: int,
    user_id: int,
    avatar_url: str,
) -> Conversation:
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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise ValueError("CONVERSATION_NOT_FOUND")

    conversation.avatar = avatar_url
    db.commit()
    db.refresh(conversation)
    return conversation


def leave_group(db: Session, conversation_id: int, user_id: int) -> None:
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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation:
        raise ValueError("CONVERSATION_NOT_FOUND")
    if conversation.type != ConversationType.GROUP:
        raise ValueError("NOT_GROUP_CONVERSATION")

    participant.left_at = datetime.utcnow()
    participant.is_admin = False
    db.commit()


def _require_group_admin(
    db: Session, conversation_id: int, user_id: int
) -> ConversationParticipant:
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

    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )
    if not conversation or conversation.type != ConversationType.GROUP:
        raise ValueError("NOT_GROUP_CONVERSATION")

    if not participant.is_admin:
        raise PermissionError("NOT_ADMIN")

    return participant


def add_group_members(
    db: Session,
    conversation_id: int,
    user_id: int,
    participant_ids: list[int],
) -> list[ParticipantOut]:
    _require_group_admin(db, conversation_id, user_id)

    if not participant_ids:
        return _get_conversation_participants(db, conversation_id)

    unique_ids = sorted({int(pid) for pid in participant_ids if pid})
    if not unique_ids:
        return _get_conversation_participants(db, conversation_id)

    existing = {
        p.user_id
        for p in db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.left_at.is_(None),
        )
        .all()
    }

    for pid in unique_ids:
        if pid in existing:
            continue
        db.add(
            ConversationParticipant(
                conversation_id=conversation_id,
                user_id=pid,
                is_admin=False,
            )
        )

    db.commit()
    return _get_conversation_participants(db, conversation_id)


def set_member_admin(
    db: Session,
    conversation_id: int,
    user_id: int,
    member_user_id: int,
    is_admin: bool,
) -> list[ParticipantOut]:
    _require_group_admin(db, conversation_id, user_id)

    participant = (
        db.query(ConversationParticipant)
        .filter(
            ConversationParticipant.conversation_id == conversation_id,
            ConversationParticipant.user_id == member_user_id,
            ConversationParticipant.left_at.is_(None),
        )
        .first()
    )
    if not participant:
        raise ValueError("PARTICIPANT_NOT_FOUND")

    participant.is_admin = bool(is_admin)
    db.commit()
    return _get_conversation_participants(db, conversation_id)


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

    # Với private chat: lấy avatar người đối diện từ Django profile
    private_ids = [
        conversation.id
        for conversation, _ in conversations
        if conversation.type == ConversationType.PRIVATE and not conversation.avatar
    ]
    other_user_by_conv: dict[int, int] = {}
    if private_ids:
        other_participants = (
            db.query(ConversationParticipant)
            .filter(
                ConversationParticipant.conversation_id.in_(private_ids),
                ConversationParticipant.user_id != user_id,
                ConversationParticipant.left_at.is_(None),
            )
            .all()
        )
        for participant in other_participants:
            other_user_by_conv[participant.conversation_id] = participant.user_id

        users_map = fetch_users_by_ids(list(other_user_by_conv.values()))
    else:
        users_map = {}

    results: list[ConversationOut] = []

    for conversation, last_message in conversations:
        avatar = conversation.avatar
        if (
            not avatar
            and conversation.type == ConversationType.PRIVATE
            and conversation.id in other_user_by_conv
        ):
            other_user = users_map.get(other_user_by_conv[conversation.id])
            avatar = other_user.avatar if other_user else None

        results.append(
            ConversationOut(
                id=conversation.id,
                type=conversation.type.value,
                name=conversation.name,
                avatar=avatar,
                last_message_id=last_message.id if last_message else None,
                sender_id=last_message.sender_id if last_message else None,
                message_type=last_message.type.value if last_message else None,
                content=last_message.content if last_message else None,
                reply_to_message_id=(
                    last_message.reply_to_message_id if last_message else None
                ),
                is_deleted=last_message.is_deleted if last_message else None,
                message_created_at=(
                    last_message.created_at.replace(tzinfo=timezone.utc)
                    if last_message and last_message.created_at
                    else None
                ),
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
    limit: int = 20,
    before_id: int | None = None,
) -> tuple[list[MessageOut], bool, list[ParticipantOut]]:
    if not user_is_participant(db, conversation_id, user_id):
        raise PermissionError("NOT_PARTICIPANT")

    query = (
        db.query(Message)
        .options(joinedload(Message.attachments))
        .filter(Message.conversation_id == conversation_id)
    )

    if before_id:
        query = query.filter(Message.id < before_id)

    messages = query.order_by(desc(Message.id)).limit(limit + 1).all()
    has_more = len(messages) > limit
    messages = messages[:limit]
    messages.reverse()

    participants = _get_conversation_participants(db, conversation_id)

    return [_serialize_message(m) for m in messages], has_more, participants


def create_system_message(
    db: Session,
    conversation_id: int,
    content: str,
) -> MessageOut:
    message = Message(
        conversation_id=conversation_id,
        sender_id=0,
        content=content.strip(),
        type=MessageType.SYSTEM,
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


def create_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str | None = None,
    reply_to_message_id: int | None = None,
    attachments_data: list[dict] | None = None,
) -> MessageOut:
    """
    Tạo tin nhắn text và/hoặc kèm file.

    attachments_data: danh sách dict đã upload xong lên R2, mỗi item gồm:
        file_name, file_url, mime_type, size, duration?, thumbnail_url?
    """
    if not user_is_participant(db, conversation_id, sender_id):
        raise PermissionError("NOT_PARTICIPANT")

    text = (content or "").strip() or None
    attachments_data = attachments_data or []

    if not text and not attachments_data:
        raise ValueError("EMPTY_MESSAGE")

    if reply_to_message_id is not None:
        reply_to = (
            db.query(Message)
            .filter(
                Message.id == reply_to_message_id,
                Message.conversation_id == conversation_id,
            )
            .first()
        )
        if not reply_to:
            raise ValueError("REPLY_MESSAGE_NOT_FOUND")

    message_type = _resolve_message_type(
        text,
        [a.get("mime_type") for a in attachments_data],
    )

    message = Message(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=text,
        type=message_type,
        reply_to_message_id=reply_to_message_id,
    )
    db.add(message)
    db.flush()

    for item in attachments_data:
        db.add(
            Attachment(
                message_id=message.id,
                file_name=item["file_name"],
                file_url=item["file_url"],
                mime_type=item.get("mime_type") or "application/octet-stream",
                size=item.get("size") or 0,
            )
        )

    db.commit()
    message = (
        db.query(Message)
        .options(joinedload(Message.attachments))
        .filter(Message.id == message.id)
        .first()
    )

    return _serialize_message(message)


def update_message(
    db: Session,
    conversation_id: int,
    message_id: int,
    user_id: int,
    content: str,
) -> MessageOut:
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id,
            Message.conversation_id == conversation_id,
        )
        .first()
    )
    if not message:
        raise ValueError("MESSAGE_NOT_FOUND")
    if message.sender_id != user_id:
        raise PermissionError("NOT_MESSAGE_OWNER")
    if message.is_deleted:
        raise ValueError("MESSAGE_DELETED")

    message.content = content.strip()
    db.commit()
    message = (
        db.query(Message)
        .options(joinedload(Message.attachments))
        .filter(Message.id == message.id)
        .first()
    )
    return _serialize_message(message)


def delete_message(
    db: Session,
    conversation_id: int,
    message_id: int,
    user_id: int,
) -> MessageOut:
    message = (
        db.query(Message)
        .filter(
            Message.id == message_id,
            Message.conversation_id == conversation_id,
        )
        .first()
    )
    if not message:
        raise ValueError("MESSAGE_NOT_FOUND")
    if message.sender_id != user_id:
        raise PermissionError("NOT_MESSAGE_OWNER")

    message.is_deleted = True
    message.content = "This message has been deleted by the user."
    db.commit()
    message = (
        db.query(Message)
        .options(joinedload(Message.attachments))
        .filter(Message.id == message.id)
        .first()
    )
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
