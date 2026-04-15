from django.db import models
from django.contrib.auth.models import User


class Deck(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subdecks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

