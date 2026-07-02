import logging

import httpx

from app.core.config import BACKEND_URL, INTERNAL_API_TOKEN
from app.schemas.chat import UserBrief

logger = logging.getLogger(__name__)


def fetch_users_by_ids(user_ids: list[int]) -> dict[int, UserBrief]:
    if not user_ids:
        return {}

    unique_ids = sorted(set(user_ids))
    ids_param = ",".join(str(uid) for uid in unique_ids)
    url = f"{BACKEND_URL}/api/users/batch/"
    headers = {"X-Internal-Token": INTERNAL_API_TOKEN}

    try:
        response = httpx.get(
            url,
            params={"ids": ids_param},
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        users = response.json().get("users", [])
        return {
            user["id"]: UserBrief(
                id=user["id"],
                username=user["username"],
                first_name=user.get("first_name", ""),
                last_name=user.get("last_name", ""),
            )
            for user in users
        }
    except Exception as exc:
        logger.error("Failed to fetch users from backend: %s", exc)
        return {
            uid: UserBrief(id=uid, username=f"user_{uid}")
            for uid in unique_ids
        }
