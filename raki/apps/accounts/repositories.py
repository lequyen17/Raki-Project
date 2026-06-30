from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.card.models import Card, Progress

User = get_user_model()


class UserRepository:

    @staticmethod
    def get_user_by_email(email):
        return User.objects.filter(email=email)

    @staticmethod
    def get_user_by_username(username):
        return User.objects.filter(username=username)

    @staticmethod
    def count_total_cards(user):
        return Card.objects.filter(note__deck__deck_users__user=user).count()

    @staticmethod
    def count_total_learned_cards(user):
        return Progress.objects.filter(user=user).count()

    @staticmethod
    def save_user(user):
        user.save()

    @staticmethod
    def save_profile(profile):
        profile.save()

    @staticmethod
    def create_user(
        username,
        email,
        password,
        first_name,
        last_name,
    ):
        return User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

    @staticmethod
    def get_users_with_due_cards():
        """Lấy users có ít nhất 1 card với next_review <= hôm nay"""
        today = timezone.now().date()
        return (
            User.objects
            .filter(user__next_review__lte=today)
            .distinct()
            .values("id", "email", "first_name", "last_name", "username")
        )
