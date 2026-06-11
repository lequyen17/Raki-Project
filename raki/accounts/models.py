from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    # Kết nối 1-1 với bảng User mặc định của Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=15, blank=True, null=True)
    # Các thông tin bổ sung cho App Anki
    total_learned_cards = models.IntegerField(default=0)

    coin_balance = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create profile when a new User is created"""
    if created:
        Profile.objects.create(user=instance)
