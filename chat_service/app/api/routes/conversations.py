from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.endpoints.deps import get_db
from app.core.security import get_current_user_id
from app.schemas.chat import (
    ConversationDetailOut,
    ConversationCreate,
    ConversationListResponse,
    ConversationOut,
    ConversationUpdateName,
    MembersAddBody,
    MemberAdminUpdateBody,
    GroupConversationCreate,
    MessageCreate,
    MessageListResponse,
    MessageOut,
    MessageUpdate,
    ReadConversationResponse,
)
from app.services import chat_service
from app.services import storage as storage_service
from app.services.user_client import fetch_users_by_ids
from app.ws.manager import manager

router = APIRouter(prefix="/conversations", tags=["Conversations"])

async def _broadcast_conversation_update(db: Session, conversation_id: int):
    participants = chat_service._get_conversation_participants(db, conversation_id)
    if not participants:
        return
    try:
        detail = chat_service.get_conversation_detail(db, conversation_id, participants[0].user_id)
        payload = {"type": "conversation_update", "data": ConversationDetailOut(**detail).model_dump(mode="json")}
        for p in participants:
            await manager.send_personal_message(payload, p.user_id)
    except Exception:
        pass

async def _broadcast_system_message(db: Session, conversation_id: int, message: MessageOut):
    participants = chat_service._get_conversation_participants(db, conversation_id)
    for p in participants:
        await manager.send_personal_message(
            {"type": "message", "data": message.model_dump(mode="json")}, 
            p.user_id
        )


async def _broadcast_new_message(db: Session, conversation_id: int, message: MessageOut):
    participants = chat_service._get_conversation_participants(db, conversation_id)
    for p in participants:
        await manager.send_personal_message(
            {"type": "message", "data": message.model_dump(mode="json")},
            p.user_id,
        )

@router.get("", response_model=ConversationListResponse)
def list_conversations(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    results = chat_service.list_conversations(db, user_id)
    return {"results": results}


@router.post("", response_model=ConversationOut)
async def create_conversation(
    body: ConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        conversation = chat_service.get_or_create_private_conversation(
            db, user_id, body.other_user_id
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await _broadcast_conversation_update(db, conversation.id)

    other_users = fetch_users_by_ids([body.other_user_id])
    other_user = other_users.get(body.other_user_id)

    return ConversationOut(
        id=conversation.id,
        type=conversation.type.value,
        name=conversation.name,
        avatar=other_user.avatar if other_user else None,
        last_message_id=None,
        sender_id=None,
        message_type=None,
        content=None,
        reply_to_message_id=None,
        is_deleted=None,
        message_created_at=None,
    )


@router.post("/group", response_model=ConversationOut)
async def create_group_conversation(
    body: GroupConversationCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        conversation = chat_service.create_group_conversation(
            db, user_id, body.name, body.participant_ids
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    await _broadcast_conversation_update(db, conversation.id)

    return ConversationOut(
        id=conversation.id,
        type=conversation.type.value,
        name=conversation.name,
        avatar=None,
        last_message_id=None,
        sender_id=None,
        message_type=None,
        content=None,
        reply_to_message_id=None,
        is_deleted=None,
        message_created_at=None,
    )


@router.get("/{conversation_id}/messages", response_model=MessageListResponse)
def get_messages(
    conversation_id: int,
    before_id: int | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        results, has_more, participants = chat_service.list_messages(
            db, conversation_id, user_id, limit=limit, before_id=before_id
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")

    return {"results": results, "has_more": has_more, "participants": participants}


@router.get("/{conversation_id}", response_model=ConversationDetailOut)
def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        return chat_service.get_conversation_detail(db, conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{conversation_id}", response_model=ConversationOut)
async def update_conversation_name(
    conversation_id: int,
    body: ConversationUpdateName,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        conversation = chat_service.update_group_name(
            db, conversation_id, user_id, body.name
        )
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_map = fetch_users_by_ids([user_id])
    username = user_map.get(user_id).username if user_map.get(user_id) else f"user_{user_id}"
    sys_msg = chat_service.create_system_message(db, conversation_id, f"{username} đã đổi tên đoạn chat thành '{body.name}'")
    await _broadcast_system_message(db, conversation_id, sys_msg)

    await _broadcast_conversation_update(db, conversation_id)

    return ConversationOut(
        id=conversation.id,
        type=conversation.type.value,
        name=conversation.name,
        avatar=conversation.avatar,
        last_message_id=None,
        sender_id=None,
        message_type=None,
        content=None,
        reply_to_message_id=None,
        is_deleted=None,
        message_created_at=None,
    )


@router.post("/{conversation_id}/members")
async def add_members(
    conversation_id: int,
    body: MembersAddBody,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        participants = chat_service.add_group_members(
            db, conversation_id, user_id, body.participant_ids
        )
    except PermissionError as exc:
        if str(exc) == "NOT_ADMIN":
            raise HTTPException(status_code=403, detail="NOT_ADMIN")
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_map = fetch_users_by_ids([user_id] + body.participant_ids)
    username = user_map.get(user_id).username if user_map.get(user_id) else f"user_{user_id}"
    
    added_names = [user_map.get(pid).username if user_map.get(pid) else f"user_{pid}" for pid in body.participant_ids]
    added_str = ", ".join(added_names)
    
    sys_msg = chat_service.create_system_message(db, conversation_id, f"{username} đã thêm {added_str} vào đoạn chat")
    await _broadcast_system_message(db, conversation_id, sys_msg)

    await _broadcast_conversation_update(db, conversation_id)
    return {"participants": participants}


@router.patch("/{conversation_id}/members/{member_user_id}/admin")
async def update_member_admin(
    conversation_id: int,
    member_user_id: int,
    body: MemberAdminUpdateBody,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        participants = chat_service.set_member_admin(
            db, conversation_id, user_id, member_user_id, body.is_admin
        )
    except PermissionError as exc:
        if str(exc) == "NOT_ADMIN":
            raise HTTPException(status_code=403, detail="NOT_ADMIN")
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_map = fetch_users_by_ids([user_id, member_user_id])
    username = user_map.get(user_id).username if user_map.get(user_id) else f"user_{user_id}"
    target_username = user_map.get(member_user_id).username if user_map.get(member_user_id) else f"user_{member_user_id}"
    
    if body.is_admin:
        action_msg = f"{username} đã cấp quyền quản trị viên cho {target_username}"
    else:
        action_msg = f"{username} đã thu hồi quyền quản trị viên của {target_username}"

    sys_msg = chat_service.create_system_message(db, conversation_id, action_msg)
    await _broadcast_system_message(db, conversation_id, sys_msg)

    await _broadcast_conversation_update(db, conversation_id)
    return {"participants": participants}


@router.post("/{conversation_id}/leave")
async def leave_group(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        chat_service.leave_group(db, conversation_id, user_id)
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    user_map = fetch_users_by_ids([user_id])
    username = user_map.get(user_id).username if user_map.get(user_id) else f"user_{user_id}"
    
    sys_msg = chat_service.create_system_message(db, conversation_id, f"{username} đã rời khỏi đoạn chat")
    await _broadcast_system_message(db, conversation_id, sys_msg)

    await _broadcast_conversation_update(db, conversation_id)
    return {"success": True}


@router.post("/{conversation_id}/messages", response_model=MessageOut)
async def send_message(
    conversation_id: int,
    request: Request,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    """
    Gửi tin nhắn text và/hoặc file.

    Hỗ trợ 2 kiểu request:
      1) application/json — text only (backward compatible)
         body: {"content": "...", "reply_to_message_id": null}
      2) multipart/form-data — text + file(s)
         fields: content, reply_to_message_id, files (multiple)

    File được upload lên Cloudflare R2; metadata lưu bảng `attachment`.
    Message.type tự suy ra từ mime (image/video/audio/file), hoặc text nếu không có file.
    """
    content_type = (request.headers.get("content-type") or "").lower()

    content: str | None = None
    reply_to_message_id: int | None = None
    attachments_data: list[dict] = []

    try:
        if "application/json" in content_type:
            try:
                body = MessageCreate.model_validate(await request.json())
            except Exception as exc:
                raise HTTPException(status_code=422, detail=str(exc))
            content = body.content
            reply_to_message_id = body.reply_to_message_id

        elif "multipart/form-data" in content_type:
            form = await request.form()
            raw_content = form.get("content")
            content = str(raw_content) if raw_content not in (None, "") else None

            raw_reply = form.get("reply_to_message_id")
            if raw_reply not in (None, ""):
                try:
                    reply_to_message_id = int(str(raw_reply))
                except ValueError:
                    raise HTTPException(
                        status_code=422, detail="INVALID_REPLY_TO_MESSAGE_ID"
                    )

            uploads = form.getlist("files")
            for upload in uploads:
                if not hasattr(upload, "read") or not getattr(upload, "filename", None):
                    continue
                data = await upload.read()
                if not data:
                    continue
                mime_type = getattr(upload, "content_type", None) or "application/octet-stream"
                try:
                    file_url = storage_service.upload_bytes(
                        data=data,
                        conversation_id=conversation_id,
                        filename=upload.filename or "file",
                        content_type=mime_type,
                    )
                except ValueError as exc:
                    detail = str(exc)
                    if detail == "FILE_TOO_LARGE":
                        raise HTTPException(status_code=413, detail="FILE_TOO_LARGE")
                    raise HTTPException(status_code=400, detail=detail)
                except RuntimeError as exc:
                    raise HTTPException(status_code=503, detail=str(exc))

                attachments_data.append(
                    {
                        "file_name": upload.filename or "file",
                        "file_url": file_url,
                        "mime_type": mime_type,
                        "size": len(data),
                    }
                )
        else:
            raise HTTPException(
                status_code=415,
                detail="Use application/json or multipart/form-data",
            )

        if not (content and str(content).strip()) and not attachments_data:
            raise HTTPException(status_code=400, detail="EMPTY_MESSAGE")

        new_message = chat_service.create_message(
            db,
            conversation_id,
            user_id,
            content=content,
            reply_to_message_id=reply_to_message_id,
            attachments_data=attachments_data,
        )
        await _broadcast_new_message(db, conversation_id, new_message)
        return new_message
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")


@router.patch("/{conversation_id}/messages/{message_id}", response_model=MessageOut)
async def update_message(
    conversation_id: int,
    message_id: int,
    body: MessageUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        message = chat_service.update_message(
            db, conversation_id, message_id, user_id, body.content
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        if str(exc) == "NOT_MESSAGE_OWNER":
            raise HTTPException(status_code=403, detail="NOT_MESSAGE_OWNER")
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")

    participants = chat_service._get_conversation_participants(db, conversation_id)
    for p in participants:
        await manager.send_personal_message(
            {"type": "message_update", "data": message.model_dump(mode="json")},
            p.user_id
        )
    return message


@router.delete("/{conversation_id}/messages/{message_id}", response_model=MessageOut)
async def delete_message(
    conversation_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        message = chat_service.delete_message(db, conversation_id, message_id, user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except PermissionError as exc:
        if str(exc) == "NOT_MESSAGE_OWNER":
            raise HTTPException(status_code=403, detail="NOT_MESSAGE_OWNER")
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")

    participants = chat_service._get_conversation_participants(db, conversation_id)
    for p in participants:
        await manager.send_personal_message(
            {"type": "message_update", "data": message.model_dump(mode="json")},
            p.user_id
        )

    return message


@router.post("/{conversation_id}/read", response_model=ReadConversationResponse)
async def mark_read(
    conversation_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    try:
        last_read_message_id = chat_service.mark_conversation_read(
            db, conversation_id, user_id
        )
    except PermissionError:
        raise HTTPException(status_code=403, detail="NOT_PARTICIPANT")

    seen_by_ids = []
    if last_read_message_id:
        participants = chat_service._get_conversation_participants(db, conversation_id)
        
        seen_by_ids = [
            p.user_id for p in participants
            if p.last_read_message_id is not None and p.last_read_message_id >= last_read_message_id
        ]
        
        for p in participants:
            await manager.send_personal_message(
                {
                    "type": "read_update",
                    "data": {
                        "conversation_id": conversation_id,
                        "message_id": last_read_message_id,
                        "seen_by_ids": seen_by_ids,
                    },
                },
                p.user_id
            )

    return {
        "success": True,
        "conversation_id": conversation_id,
        "last_read_message_id": last_read_message_id,
        "seen_by_ids": seen_by_ids,
    }
