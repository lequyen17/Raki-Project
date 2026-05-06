from django.db import models
from django.contrib.auth.models import User

from card.models import Card


class Progress(models.Model):
    # Liên kết với User (ai đang học?)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")

    # Liên kết với Card (đang học thẻ nào?)
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name="card")

    # Thuật toán Spaced Repetition (thường là SM-2)
    status = models.CharField(
        max_length=20,
        choices=[
            ("new", "New"),
            ("learning", "Learning"),
            ("review", "Review"),
        ],
        default="learning",
    )

    # Khoảng thời gian giữa các lần ôn tập (tính bằng ngày)
    interval = models.IntegerField(default=1)

    # Số lần lặp lại liên tiếp thành công
    repetition = models.IntegerField(default=0)

    # Độ dễ của thẻ (thường bắt đầu ở mức 2.5)
    easiness = models.FloatField(default=2.5)

    # Ngày tiếp theo cần ôn tập
    next_review = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Đảm bảo một user chỉ có một bản ghi progress cho mỗi card
        unique_together = ("user", "card")

    def __str__(self):
        return f"User: {self.user.username} - Card ID: {self.card.id} - Next: {self.next_review}"
