from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import validate_email
from rest_framework import serializers

from .repositories import UserRepository


class UserProfileUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)

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
            try:
                validate_email(email)
            except DjangoValidationError:
                raise serializers.ValidationError("Email không hợp lệ")

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():
                raise serializers.ValidationError("Email này đã được đăng ký")

        if first_name and (len(first_name) < 2 or len(first_name) > 150):
            raise serializers.ValidationError("Tên đầu phải từ 2 đến 150 ký tự")

        if last_name and (len(last_name) < 2 or len(last_name) > 150):
            raise serializers.ValidationError("Họ phải từ 2 đến 150 ký tự")

        if phone and len(phone) > 15:
            raise serializers.ValidationError("Số điện thoại không hợp lệ")

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True, max_length=15)

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password", "").strip()
        confirm_password = attrs.get("confirm_password", "").strip()
        email = attrs.get("email", "").strip()
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()
        phone = attrs.get("phone", "").strip()

        if not all(
            [username, password, confirm_password, email, first_name, last_name]
        ):
            raise serializers.ValidationError(
                "Vui lòng điền đầy đủ tất cả các trường bắt buộc"
            )

        if len(username) < 3:
            raise serializers.ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự")

        if len(username) > 150:
            raise serializers.ValidationError(
                "Tên đăng nhập không được vượt quá 150 ký tự"
            )

        if UserRepository.get_user_by_username(username).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại")

        try:
            validate_email(email)
        except DjangoValidationError:
            raise serializers.ValidationError("Email không hợp lệ")

        if UserRepository.get_user_by_email(email).exists():
            raise serializers.ValidationError("Email này đã được đăng ký")

        if len(password) < 6:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 6 ký tự")

        if password != confirm_password:
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp")

        if len(first_name) < 2 or len(first_name) > 150:
            raise serializers.ValidationError("Tên đầu phải từ 2 đến 150 ký tự")

        if len(last_name) < 2 or len(last_name) > 150:
            raise serializers.ValidationError("Họ phải từ 2 đến 150 ký tự")

        if phone and len(phone) > 15:
            raise serializers.ValidationError("Số điện thoại không hợp lệ")

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


class RegisterResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = RegisteredUserSerializer()


class ProfileUpdateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    user = UserProfileSerializer()
