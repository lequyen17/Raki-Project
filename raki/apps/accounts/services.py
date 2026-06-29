import json
import logging
import random
import string

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from config.redis_client import redis_client
from .repositories import UserRepository

logger = logging.getLogger(__name__)

OTP_TTL = 300  # 5 phút
OTP_KEY_PREFIX = "otp_registration:"


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
        """Gửi email chứa mã OTP xác thực"""
        name = first_name or "bạn"
        subject = "Mã OTP xác thực đăng ký Raki"
        message = (
            f"Xin chào {name},\n\n"
            f"Mã OTP xác thực tài khoản của bạn là: {otp}\n\n"
            f"Mã có hiệu lực trong 5 phút. Vui lòng không chia sẻ mã này với ai.\n\n"
            f"Trân trọng,\nĐội ngũ Raki"
        )
        html_message = (
            f"<h2>Xin chào {name}! 👋</h2>"
            f"<p>Cảm ơn bạn đã đăng ký tài khoản trên <strong>Raki</strong>.</p>"
            f"<p>Mã OTP xác thực của bạn là:</p>"
            f"<div style='font-size:32px;font-weight:bold;letter-spacing:10px;"
            f"background:#f0f4ff;padding:16px 24px;border-radius:8px;"
            f"display:inline-block;margin:12px 0;color:#3b82f6;'>"
            f"{otp}</div>"
            f"<p>Mã có hiệu lực trong <strong>5 phút</strong>.</p>"
            f"<p style='color:#888;font-size:13px;'>Vui lòng không chia sẻ mã này với bất kỳ ai.</p>"
            f"<br><p>Trân trọng,<br><strong>Đội ngũ Raki</strong></p>"
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info("OTP email sent to %s", email)
        except Exception as exc:
            logger.error("Failed to send OTP email to %s: %s", email, exc)
            raise

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
        """Gửi email chào mừng sau khi đăng ký thành công"""
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username
        subject = "Chào mừng bạn đến với Raki! 🎉"
        message = (
            f"Xin chào {full_name},\n\n"
            f"Tài khoản của bạn đã được tạo thành công trên Raki.\n"
            f"Tên đăng nhập: {user.username}\n\n"
            f"Bắt đầu học ngay và chinh phục mọi bộ flashcard của bạn!\n\n"
            f"Trân trọng,\nĐội ngũ Raki"
        )
        html_message = (
            f"<h2>Xin chào {full_name}! 👋</h2>"
            f"<p>Tài khoản của bạn đã được tạo thành công trên <strong>Raki</strong>.</p>"
            f"<ul>"
            f"  <li><strong>Tên đăng nhập:</strong> {user.username}</li>"
            f"  <li><strong>Email:</strong> {user.email}</li>"
            f"</ul>"
            f"<p>Bắt đầu học ngay và chinh phục mọi bộ flashcard của bạn!</p>"
            f"<br><p>Trân trọng,<br><strong>Đội ngũ Raki</strong></p>"
        )
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            logger.info("Welcome email sent to %s", user.email)
        except Exception as exc:
            logger.error("Failed to send welcome email to %s: %s", user.email, exc)
