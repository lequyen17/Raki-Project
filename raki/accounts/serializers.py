from rest_framework import serializers
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from .repositories import UserRepository


class UserProfileUpdateSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        user = self.user
        email = attrs.get("email", user.email).strip()
        first_name = attrs.get("first_name", user.first_name).strip()
        last_name = attrs.get("last_name", user.last_name).strip()
        
        try:
            phone = attrs.get("phone", user.profile.phone or "").strip()
        except AttributeError:
            phone = attrs.get("phone", "").strip()

        # Validate email
        if email != user.email:
            try:
                validate_email(email)
            except ValidationError:
                raise serializers.ValidationError("Email không hợp lệ")

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():
                raise serializers.ValidationError("Email này đã được đăng ký")

        # Validate first_name
        if first_name and (len(first_name) < 2 or len(first_name) > 150):
            raise serializers.ValidationError("Tên đầu phải từ 2 đến 150 ký tự")

        # Validate last_name
        if last_name and (len(last_name) < 2 or len(last_name) > 150):
            raise serializers.ValidationError("Họ phải từ 2 đến 150 ký tự")

        # Validate phone
        if phone and len(phone) > 15:
            raise serializers.ValidationError("Số điện thoại không hợp lệ")

        # Return validated and cleaned data
        attrs["email"] = email
        attrs["first_name"] = first_name
        attrs["last_name"] = last_name
        attrs["phone"] = phone
        return attrs


class UserRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, allow_blank=False)
    confirm_password = serializers.CharField(required=True, allow_blank=False)
    email = serializers.CharField(required=True, allow_blank=False)
    first_name = serializers.CharField(required=True, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_blank=False)
    phone = serializers.CharField(required=True, allow_blank=False)

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        password = attrs.get("password", "").strip()
        confirm_password = attrs.get("confirm_password", "").strip()
        email = attrs.get("email", "").strip()
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()
        phone = attrs.get("phone", "").strip()

        # Validate required fields
        if not all([username, password, confirm_password, email, first_name, last_name]):
            raise serializers.ValidationError("Vui lòng điền đầy đủ tất cả các trường bắt buộc")

        # Validate username
        if len(username) < 3:
            raise serializers.ValidationError("Tên đăng nhập phải có ít nhất 3 ký tự")

        if len(username) > 150:
            raise serializers.ValidationError("Tên đăng nhập không được vượt quá 150 ký tự")

        if UserRepository.get_user_by_username(username).exists():
            raise serializers.ValidationError("Tên đăng nhập đã tồn tại")

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            raise serializers.ValidationError("Email không hợp lệ")

        if UserRepository.get_user_by_email(email).exists():
            raise serializers.ValidationError("Email này đã được đăng ký")

        # Validate password
        if len(password) < 6:
            raise serializers.ValidationError("Mật khẩu phải có ít nhất 6 ký tự")

        if password != confirm_password:
            raise serializers.ValidationError("Mật khẩu xác nhận không khớp")

        # Validate names
        if len(first_name) < 2 or len(first_name) > 150:
            raise serializers.ValidationError("Tên đầu phải từ 2 đến 150 ký tự")

        if len(last_name) < 2 or len(last_name) > 150:
            raise serializers.ValidationError("Họ phải từ 2 đến 150 ký tự")

        # Validate phone
        if phone and len(phone) > 15:
            raise serializers.ValidationError("Số điện thoại không hợp lệ")

        attrs["username"] = username
        attrs["password"] = password
        attrs["email"] = email
        attrs["first_name"] = first_name
        attrs["last_name"] = last_name
        attrs["phone"] = phone
        return attrs
