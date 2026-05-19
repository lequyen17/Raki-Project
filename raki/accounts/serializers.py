from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .repositories import UserRepository


class UserProfileValidator:

    @staticmethod
    def validate_update(data, user):

        email = data.get("email", user.email).strip()
        first_name = data.get("first_name", user.first_name).strip()
        last_name = data.get("last_name", user.last_name).strip()

        try:
            phone = data.get("phone", user.profile.phone or "").strip()
        except AttributeError:
            phone = data.get("phone", "").strip()

        # Validate email
        if email != user.email:

            try:
                validate_email(email)
            except ValidationError:
                raise ValueError("Email không hợp lệ")

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():
                raise ValueError("Email này đã được đăng ký")

        # Validate first_name
        if first_name and (len(first_name) < 2 or len(first_name) > 150):
            raise ValueError("Tên đầu phải từ 2 đến 150 ký tự")

        # Validate last_name
        if last_name and (len(last_name) < 2 or len(last_name) > 150):
            raise ValueError("Họ phải từ 2 đến 150 ký tự")

        # Validate phone
        if phone and len(phone) > 15:
            raise ValueError("Số điện thoại không hợp lệ")

        return {
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }


class UserRegistrationValidator:

    @staticmethod
    def validate(data):

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()
        email = data.get("email", "").strip()
        first_name = data.get("first_name", "").strip()
        last_name = data.get("last_name", "").strip()
        phone = data.get("phone", "").strip()

        # Required fields
        if not all(
            [
                username,
                password,
                confirm_password,
                email,
                first_name,
                last_name,
            ]
        ):
            raise ValueError("Vui lòng điền đầy đủ tất cả các trường bắt buộc")

        # Username
        if len(username) < 3:
            raise ValueError("Tên đăng nhập phải có ít nhất 3 ký tự")

        if len(username) > 150:
            raise ValueError("Tên đăng nhập không được vượt quá 150 ký tự")

        if UserRepository.get_user_by_username(username).exists():
            raise ValueError("Tên đăng nhập đã tồn tại")

        # Email
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("Email không hợp lệ")

        if UserRepository.get_user_by_email(email).exists():
            raise ValueError("Email này đã được đăng ký")

        # Password
        if len(password) < 6:
            raise ValueError("Mật khẩu phải có ít nhất 6 ký tự")

        if password != confirm_password:
            raise ValueError("Mật khẩu xác nhận không khớp")

        # Names
        if len(first_name) < 2 or len(first_name) > 150:
            raise ValueError("Tên đầu phải từ 2 đến 150 ký tự")

        if len(last_name) < 2 or len(last_name) > 150:
            raise ValueError("Họ phải từ 2 đến 150 ký tự")

        # Phone
        if phone and len(phone) > 15:
            raise ValueError("Số điện thoại không hợp lệ")

        return {
            "username": username,
            "password": password,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "phone": phone,
        }
