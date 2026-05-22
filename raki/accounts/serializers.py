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
                message="Phone number must start with 0 and be exactly 10 digits long.",
            )
        ],
    )

    def validate(self, attrs):
        user = self.context["user"]

        email = str(attrs.get("email", user.email)).strip()
        first_name = str(attrs.get("first_name", user.first_name)).strip()
        last_name = str(attrs.get("last_name", user.last_name)).strip()

        try:
            phone = str(attrs.get("phone", user.profile.phone or "")).strip()
        except AttributeError:
            phone = str(attrs.get("phone", "")).strip()

        if email != user.email:

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():
                raise serializers.ValidationError("Email has already been taken.")

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
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
                message="Phone number must start with 0 and be exactly 10 digits long.",
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
            raise serializers.ValidationError("Username has already been taken.")

        if UserRepository.get_user_by_email(email).exists():
            raise serializers.ValidationError("Email has already been taken.")

        if password != confirm_password:
            raise serializers.ValidationError("Confirm password does not match.")

        return {
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }


# --- OpenAPI response schemas ---


class CurrentUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()


class UserProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    phone = serializers.CharField()
    total_cards = serializers.IntegerField()
    total_learned_cards = serializers.IntegerField()
    is_staff = serializers.BooleanField()


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
