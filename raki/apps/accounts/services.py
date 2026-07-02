import json
import logging
import random
import string

import httpx
from django.conf import settings
from django.db import transaction

from config.redis_client import redis_client
from .repositories import UserRepository

logger = logging.getLogger(__name__)

OTP_TTL = 300  # 5 phút
OTP_KEY_PREFIX = "otp_registration:"


def _call_mail_service(endpoint: str, payload: dict):
    """Gọi HTTP POST đến mail service. Raises nếu thất bại."""
    url = f"{settings.MAIL_SERVICE_URL}{endpoint}"
    try:
        response = httpx.post(url, json=payload, timeout=10)
        response.raise_for_status()
        logger.info("Mail service called successfully: %s", endpoint)
    except httpx.RequestError as exc:
        logger.error("Mail service connection error [%s]: %s", endpoint, exc)
        raise
    except httpx.HTTPStatusError as exc:
        logger.error(
            "Mail service HTTP error [%s]: %s — %s",
            endpoint,
            exc.response.status_code,
            exc.response.text,
        )
        raise


class UserService:

    @staticmethod
    def get_user_profile_data(user):
        """Logic lấy thông tin profile và cập nhật số thẻ đã học"""
        total_cards = UserRepository.count_total_cards(user)
        total_learned_cards = UserRepository.count_total_learned_cards(user)

        try:
            profile = user.profile
            # Logic nghiệp vụ: Cập nhật nếu số lượng thay đổi
            if profile.total_learned_cards != total_learned_cards:
                profile.total_learned_cards = total_learned_cards
                profile.save(update_fields=["total_learned_cards"])
            phone = profile.phone
        except AttributeError:
            phone = ""
            total_learned_cards = 0

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": phone,
            "total_cards": total_cards,
            "total_learned_cards": total_learned_cards,
            "is_staff": user.is_staff,
        }

    @staticmethod
    @transaction.atomic
    def update_user_profile(user, validated_data):
        """Logic cập nhật thông tin user và profile"""
        # Update User
        user.email = validated_data["email"]
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.save()

        # Update Profile
        profile = user.profile
        profile.phone = validated_data["phone"]
        profile.save()

        # Lấy lại dữ liệu mới nhất để trả về
        profile_data = UserService.get_user_profile_data(user)
        return {
            "success": True,
            "message": "Cập nhật hồ sơ thành công!",
            "user": profile_data,
        }

    # ------------------------------------------------------------------
    # OTP Registration Flow
    # ------------------------------------------------------------------

    @staticmethod
    def _generate_otp(length=6):
        """Tạo mã OTP gồm các chữ số ngẫu nhiên"""
        return "".join(random.choices(string.digits, k=length))

    @staticmethod
    def _redis_key(email: str) -> str:
        return f"{OTP_KEY_PREFIX}{email}"

    @staticmethod
    def send_otp_email(email: str, otp: str, first_name: str = ""):
        """Gửi email OTP qua mail service"""
        _call_mail_service(
            "/mail/otp",
            {
                "to": email,
                "otp": otp,
                "first_name": first_name or "bạn",
            },
        )

    @staticmethod
    def initiate_registration(validated_data: dict):
        """
        Bước 1: Validate xong, tạo OTP, lưu thông tin đăng ký vào Redis,
        gửi email OTP. Chưa tạo tài khoản.
        """
        otp = UserService._generate_otp()
        key = UserService._redis_key(validated_data["email"])

        payload = {**validated_data, "otp": otp}
        redis_client.setex(key, OTP_TTL, json.dumps(payload))

        UserService.send_otp_email(
            email=validated_data["email"],
            otp=otp,
            first_name=validated_data.get("first_name", ""),
        )
        return {"message": "OTP_SENT"}

    @staticmethod
    @transaction.atomic
    def verify_otp_and_register(email: str, otp_input: str):
        """
        Bước 2: Xác thực OTP từ Redis, tạo tài khoản, gửi mail chào mừng.
        """
        key = UserService._redis_key(email)
        raw = redis_client.get(key)

        if raw is None:
            raise ValueError("OTP_EXPIRED")

        payload = json.loads(raw)
        stored_otp = payload.get("otp", "")

        if otp_input != stored_otp:
            raise ValueError("OTP_INVALID")

        # Xóa key khỏi Redis ngay sau khi xác thực thành công
        redis_client.delete(key)

        # Tạo tài khoản
        user = UserRepository.create_user(
            username=payload["username"],
            email=payload["email"],
            password=payload["password"],
            first_name=payload["first_name"],
            last_name=payload["last_name"],
        )

        profile = user.profile
        profile.phone = payload.get("phone", "")
        profile.save()

        # Gửi email chào mừng (không ảnh hưởng transaction nếu thất bại)
        UserService.send_welcome_email(user)

        return {
            "success": True,
            "message": "Đăng ký thành công!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": profile.phone,
            },
        }

    @staticmethod
    def send_welcome_email(user):
        """Gửi email chào mừng qua mail service sau khi đăng ký thành công"""
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        try:
            _call_mail_service(
                "/mail/welcome",
                {
                    "to": user.email,
                    "username": user.username,
                    "full_name": full_name,
                },
            )
        except Exception as exc:
            # Welcome email không block quá trình đăng ký
            logger.error("Failed to send welcome email to %s: %s", user.email, exc)

    @staticmethod
    def get_users_with_due_cards():
        """Lấy danh sách users có ít nhất 1 card cần ôn tập"""
        return list(UserRepository.get_users_with_due_cards())

    @staticmethod
    def get_users_by_ids(user_ids):
        return list(UserRepository.get_users_by_ids(user_ids))
