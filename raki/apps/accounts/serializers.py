from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator, validate_email
from rest_framework import serializers

from .repositories import UserRepository


class UserProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(
        required=False, allow_blank=True, max_length=150, min_length=2
    )
    last_name = serializers.CharField(
        required=False, allow_blank=True, max_length=150, min_length=2
    )
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
        min_length=10,
        validators=[
            RegexValidator(
                regex=r"^0\d{9}$",
                message="PHONE_INVALID_FORMAT",
            )
        ],
    )
    # CharField thay vì URLField: URL R2 có thể dài / dạng public domain
    # không luôn pass Django URLValidator mặc định.
    avatar = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, max_length=500
    )

    def validate(self, attrs):
        user = self.context["user"]

        email = str(attrs.get("email", user.email)).strip()
        first_name = str(attrs.get("first_name", user.first_name)).strip()
        last_name = str(attrs.get("last_name", user.last_name)).strip()

        try:
            phone = str(attrs.get("phone", user.profile.phone or "")).strip()
            current_avatar = user.profile.avatar or ""
        except AttributeError:
            phone = str(attrs.get("phone", "")).strip()
            current_avatar = ""

        if "avatar" in attrs:
            avatar_raw = attrs.get("avatar")
            avatar = str(avatar_raw).strip() if avatar_raw else ""
        else:
            avatar = current_avatar

        if email != user.email:

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():
                raise serializers.ValidationError("EMAIL_TAKEN")

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
            "avatar": avatar or None,
        }


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, min_length=3)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, min_length=2)
    last_name = serializers.CharField(max_length=150, min_length=2)
    phone = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=10,
        min_length=10,
        validators=[
            RegexValidator(
                regex=r"^0\d{9}$",
                message="PHONE_INVALID_FORMAT",
            )
        ],
    )

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password", "").strip()
        confirm_password = attrs.get("confirm_password", "").strip()
        email = attrs.get("email", "").strip()
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()
        phone = attrs.get("phone", "").strip()

        if UserRepository.get_user_by_username(username).exists():
            raise serializers.ValidationError("USERNAME_TAKEN")

        if UserRepository.get_user_by_email(email).exists():
            raise serializers.ValidationError("EMAIL_TAKEN")

        if password != confirm_password:
            raise serializers.ValidationError("CONFIRM_PASSWORD_MISMATCH")

        return {
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }


class OtpVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(min_length=6, max_length=6)

# --- OpenAPI response schemas ---


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    avatar = serializers.URLField(allow_null=True, required=False)


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    avatar = serializers.URLField(allow_null=True, required=False)
    total_cards = serializers.IntegerField()
    total_learned_cards = serializers.IntegerField()
    is_staff = serializers.BooleanField()


class AvatarUploadResponseSerializer(serializers.Serializer):
    avatar = serializers.URLField()


class RegisteredUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()


class RegisterResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = RegisteredUserSerializer()


class ProfileUpdateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = UserProfileSerializer()


class DueUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    username = serializers.CharField()


class DueUsersResponseSerializer(serializers.Serializer):
    users = DueUserSerializer(many=True)


class BatchUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    avatar = serializers.URLField(allow_null=True, required=False)


class BatchUsersResponseSerializer(serializers.Serializer):
    users = BatchUserSerializer(many=True)
