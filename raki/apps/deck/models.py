from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    SHARE_MODE_CHOICES = [
        ("private", "Private"),
        ("public", "Public"),
        ("restricted", "Restricted"),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="subdecks"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    share_mode = models.CharField(
        max_length=20, choices=SHARE_MODE_CHOICES, default="private"
    )
    coin_price = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserDeck(models.Model):
    # Định nghĩa các vai trò trong một bộ thẻ
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("viewer", "Viewer"),
        ("editor", "Editor"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_decks")

    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name="deck_users")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="viewer")

    class Meta:
        # Đảm bảo một user không bị trùng lặp vai trò trong cùng một deck
        unique_together = ("user", "deck")

    def __str__(self):
        return f"{self.user.username} - {self.deck.name} ({self.role})"
