from django.db import models
from django.contrib.auth.models import User

# Import model Deck từ app chứa nó (giả sử app tên là 'decks')
# Bạn hãy điều chỉnh lại đường dẫn import cho đúng cấu trúc thư mục của mình nhé
from apps.deck.models import Deck


# Create your models here.
class CoinTransaction(models.Model):
    # Khóa ngoại liên kết tới bộ thẻ (Một Deck có thể có nhiều giao dịch mua)
    deck = models.ForeignKey(
        Deck, on_delete=models.CASCADE, related_name="coin_transactions"
    )

    # Khóa ngoại liên kết tới User mua thẻ (buyer_id)
    buyer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="buyer_transactions"
    )

    # Tổng số xu người mua phải trả (Giá gốc của Deck)
    coin = models.PositiveIntegerField()

    # Thời gian diễn ra giao dịch
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]  # Sắp xếp giao dịch mới nhất lên đầu

    def __str__(self):
        return f"Tx #{self.id}: {self.buyer.username} bought {self.deck.name} for {self.coin} coins"


class PaymentHistory(models.Model):
    # Các trạng thái có thể có của một giao dịch nạp tiền
    STATUS_CHOICES = [
        ("pending", "Pending"),  # Đang chờ thanh toán
        ("completed", "Completed"),  # Thành công
        ("failed", "Failed"),  # Thất bại
        ("canceled", "Canceled"),  # Hủy bỏ
    ]

    # Khóa ngoại liên kết tới User thực hiện nạp tiền
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="payment_histories"
    )

    # Số tiền nạp thực tế bằng VND (sử dụng DecimalField để chính xác tuyệt đối về tiền tệ)
    amount_vnd = models.DecimalField(max_digits=12, decimal_places=2)

    # Số lượng xu nhận được tương ứng sau khi nạp thành công
    coin_received = models.PositiveIntegerField()

    # Trạng thái của giao dịch thanh toán
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Thời gian tạo yêu cầu nạp tiền
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Payment Histories"

    def __str__(self):
        return f"Payment #{self.id} - {self.user.username}: {self.amount_vnd} VND ({self.status})"


class CoinHistory(models.Model):
    REASON_CHOICES = [
        ("TOPUP", "Top Up"),
        ("BUY_DECK", "Buy Deck"),
        ("SELL_DECK", "Sell Deck"),
        ("DAILY_LOGIN", "Daily Login"),
        ("EVENT_REWARD", "Event Reward"),
        ("REFUND", "Refund"),
    ]
    # Khóa ngoại liên kết tới User bị biến động số dư xu
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="coin_histories"
    )

    # Số lượng xu thay đổi.
    # Mẹo: Nên dùng IntegerField (có thể âm hoặc dương) để dễ quản lý.
    # Ví dụ: +100 (khi nạp xu), -50 (khi mua bộ thẻ)
    amount = models.IntegerField()

    # Lý do biến động số dư (Ví dụ: "Nạp tiền qua VNPay", "Mua bộ thẻ Oxford", "Nhận tiền bán thẻ",...)
    reason = models.CharField(max_length=100, choices=REASON_CHOICES)

    # Thời gian biến động số dư xu
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Coin Histories"

    def __str__(self):
        sign = "+" if self.amount >= 0 else ""
        return f"Coin Change #{self.id} - {self.user.username}: {sign}{self.amount} xu ({self.reason})"
