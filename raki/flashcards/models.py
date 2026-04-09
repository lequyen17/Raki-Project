from django.db import models
from django.contrib.auth.models import User

# 1. Bảng Deck (Bộ thẻ) - Thuộc về 1 User
class Deck(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='decks')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subdecks')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. Bảng Card (Thẻ) - Thuộc về 1 Deck
class Card(models.Model):
    deck = models.ForeignKey(Deck, on_delete=models.CASCADE, related_name='cards')
    front = models.TextField() # Mặt trước
    back = models.TextField()  # Mặt sau
    
    # Logic Anki
    next_review = models.DateTimeField(auto_now_add=True) # Ngày hẹn học lại
    interval = models.IntegerField(default=0) # Khoảng cách ngày học
    easiness = models.FloatField(default=2.5)  # Độ dễ của thẻ (mặc định 2.5)
    repetition = models.IntegerField(default=0) # Số lần đã học liên tiếp thành công
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Card: {self.front[:20]}"