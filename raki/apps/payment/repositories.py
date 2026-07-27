from django.db import transaction
from apps.payment.models import CoinHistory


class WalletRepository:

    @staticmethod
    def get_coin_balance(user):
        try:
            return user.profile.coin_balance
        except AttributeError:
            return 0

    @staticmethod
    def get_coin_histories(user):
        return CoinHistory.objects.filter(user=user)

    @staticmethod
    def add_coin(user, amount, reason="TOPUP", reference_id=None):
        """
        Cộng coin cho user và tạo CoinHistory.
        Được gọi khi Payment Service xác nhận giao dịch thành công.
        """
        with transaction.atomic():
            profile = user.profile
            profile.coin_balance += amount
            profile.save(update_fields=["coin_balance"])

            CoinHistory.objects.create(
                user=user,
                amount=amount,
                reason=reason,
                reference_id=reference_id,
            )
