"""Upload file lên Cloudflare R2 (S3-compatible API)."""

from __future__ import annotations

import logging
import uuid
from pathlib import PurePosixPath

import boto3
from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

from app.core import config

logger = logging.getLogger(__name__)


def _require_r2_config() -> None:
    missing = [
        name
        for name, value in (
            ("R2_ENDPOINT_URL", config.R2_ENDPOINT_URL),
            ("R2_ACCESS_KEY_ID", config.R2_ACCESS_KEY_ID),
            ("R2_SECRET_ACCESS_KEY", config.R2_SECRET_ACCESS_KEY),
            ("R2_BUCKET_NAME", config.R2_BUCKET_NAME),
            ("R2_PUBLIC_URL", config.R2_PUBLIC_URL),
        )
        if not value
    ]
    if missing:
        raise RuntimeError(
            "Cloudflare R2 chưa được cấu hình. "
            f"Điền các biến môi trường: {', '.join(missing)}"
        )


def _get_r2_client():
    _require_r2_config()
    return boto3.client(
        "s3",
        endpoint_url=config.R2_ENDPOINT_URL,
        aws_access_key_id=config.R2_ACCESS_KEY_ID,
        aws_secret_access_key=config.R2_SECRET_ACCESS_KEY,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )


def _build_object_key(
    conversation_id: int,
    original_filename: str,
) -> str:
    safe_name = PurePosixPath(original_filename or "file").name
    return f"chat/{conversation_id}/{uuid.uuid4().hex}_{safe_name}"


def upload_bytes(
    *,
    data: bytes,
    conversation_id: int,
    filename: str,
    content_type: str | None = None,
) -> str:
    """
    Upload binary lên R2 và trả về public URL.

    Returns:
        Public URL của file (R2_PUBLIC_URL + object key).
    """
    if not data:
        raise ValueError("EMPTY_FILE")

    if len(data) > config.MAX_UPLOAD_SIZE:
        raise ValueError("FILE_TOO_LARGE")

    key = _build_object_key(conversation_id, filename)
    client = _get_r2_client()

    extra_args: dict = {}
    if content_type:
        extra_args["ContentType"] = content_type

    try:
        client.put_object(
            Bucket=config.R2_BUCKET_NAME,
            Key=key,
            Body=data,
            **extra_args,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.exception("R2 upload failed: %s", exc)
        raise RuntimeError("R2_UPLOAD_FAILED") from exc

    public_base = config.R2_PUBLIC_URL.rstrip("/")
    return f"{public_base}/{key}"
