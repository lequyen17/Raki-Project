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
            "user": user,
            "phone": phone,
            "total_cards": total_cards,
            "total_learned_cards": total_learned_cards,
        }

    @staticmethod
    @transaction.atomic
    def update_user_profile(user, data):
        """Logic cập nhật thông tin user và profile"""
        # Update User
        user.email = data["email"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.save()

        # Update Profile
        profile = user.profile
        profile.phone = data["phone"]
        profile.save()

        # Lấy lại dữ liệu mới nhất để trả về
        return UserService.get_user_profile_data(user)

    @staticmethod
    @transaction.atomic
    def register_user(data):
        """Logic đăng ký user mới"""
        user = UserRepository.create_user(
            username=data["username"],
            email=data["email"],
            password=data["password"],
            first_name=data["first_name"],
            last_name=data["last_name"],
        )

        profile = user.profile
        profile.phone = data["phone"]
        profile.save()

        return user
