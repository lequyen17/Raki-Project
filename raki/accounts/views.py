from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from accounts.repositories.user_repository import UserRepository


class UserService:

    @staticmethod
    def get_profile(user):

        total_cards = UserRepository.count_total_cards(user)

        try:
            profile = user.profile

            total_learned_cards = UserRepository.count_total_learned_cards(user)

            if profile.total_learned_cards != total_learned_cards:
                profile.total_learned_cards = total_learned_cards
                UserRepository.save_profile(profile)

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
            "groups": list(user.groups.values_list("name", flat=True)),
        }

    @staticmethod
    def update_profile(user, data):

        email = data.get("email", user.email).strip()
        first_name = data.get("first_name", user.first_name).strip()

        last_name = data.get("last_name", user.last_name).strip()

        phone = data.get("phone", user.profile.phone or "").strip()

        # Validate email
        if email != user.email:

            try:
                validate_email(email)
            except ValidationError:
                raise Exception("Email không hợp lệ")

            if UserRepository.get_user_by_email(email).exclude(id=user.id).exists():

                raise Exception("Email này đã được đăng ký")

        # Validate first name
        if first_name and (len(first_name) < 2 or len(first_name) > 150):
            raise Exception("Tên đầu phải từ 2 đến 150 ký tự")

        # Validate last name
        if last_name and (len(last_name) < 2 or len(last_name) > 150):
            raise Exception("Họ phải từ 2 đến 150 ký tự")

        # Validate phone
        if phone and len(phone) > 15:
            raise Exception("Số điện thoại không hợp lệ")

        # Update user
        user.email = email
        user.first_name = first_name
        user.last_name = last_name

        UserRepository.save_user(user)

        # Update profile
        profile = user.profile
        profile.phone = phone

        UserRepository.save_profile(profile)

        total_cards = UserRepository.count_total_cards(user)

        total_learned_cards = UserRepository.count_total_learned_cards(user)

        return {
            "success": True,
            "message": "Cập nhật hồ sơ thành công!",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone": profile.phone,
                "total_cards": total_cards,
                "total_learned_cards": total_learned_cards,
            },
        }

    @staticmethod
    def register(data):

        username = data.get("username", "").strip()
        password = data.get("password", "").strip()

        confirm_password = data.get("confirm_password", "").strip()

        email = data.get("email", "").strip()

        first_name = data.get("first_name", "").strip()

        last_name = data.get("last_name", "").strip()

        phone = data.get("phone", "").strip()

        # Validate required
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
            raise Exception("Vui lòng điền đầy đủ tất cả các trường bắt buộc")

        # Username
        if len(username) < 3:
            raise Exception("Tên đăng nhập phải có ít nhất 3 ký tự")

        if len(username) > 150:
            raise Exception("Tên đăng nhập không được vượt quá 150 ký tự")

        if UserRepository.get_user_by_username(username).exists():
            raise Exception("Tên đăng nhập đã tồn tại")

        # Email
        try:
            validate_email(email)
        except ValidationError:
            raise Exception("Email không hợp lệ")

        if UserRepository.get_user_by_email(email).exists():
            raise Exception("Email này đã được đăng ký")

        # Password
        if len(password) < 6:
            raise Exception("Mật khẩu phải có ít nhất 6 ký tự")

        if password != confirm_password:
            raise Exception("Mật khẩu xác nhận không khớp")

        # Name validate
        if len(first_name) < 2 or len(first_name) > 150:
            raise Exception("Tên đầu phải từ 2 đến 150 ký tự")

        if len(last_name) < 2 or len(last_name) > 150:
            raise Exception("Họ phải từ 2 đến 150 ký tự")

        # Phone
        if phone and len(phone) > 15:
            raise Exception("Số điện thoại không hợp lệ")

        # Create user
        user = UserRepository.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        profile = user.profile
        profile.phone = phone

        UserRepository.save_profile(profile)

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
