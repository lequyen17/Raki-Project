from django.db import transaction
from .repositories import UserRepository


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

    @staticmethod
    @transaction.atomic
    def register_user(validated_data):
        """Logic đăng ký user mới"""
        user = UserRepository.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )

        profile = user.profile
        profile.phone = validated_data.get("phone", "")
        profile.save()

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
