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
    def get_payment_histories(user):
        # return PaymentHistory.objects.filter(user=user)
        return CoinHistory.objects.filter(user=user)


class PaymentRepository:

    @staticmethod
    def create_payment(user, amount_vnd, coin_received, status="pending"):
        # return PaymentHistory.objects.create(
        #     user=user,
        #     amount_vnd=amount_vnd,
        #     coin_received=coin_received,
        #     status=status,
        # )
        return CoinHistory.objects.filter(user=user)

    @staticmethod
    def get_payment_by_id(payment_id, for_update=False):
        # qs = PaymentHistory.objects
        # if for_update:
        #     qs = qs.select_for_update()
        # return qs.get(id=payment_id)
        return CoinHistory.objects.filter(user=user)

    @staticmethod
    def update_payment_status(payment, status):
        payment.status = status
        payment.save(update_fields=["status"])
        return payment

    @staticmethod
    def mark_payment_completed(payment):
        payment.status = "completed"
        payment.save(update_fields=["status"])

        profile = payment.user.profile
        profile.coin_balance += payment.coin_received
        profile.save(update_fields=["coin_balance"])

        CoinHistory.objects.create(
            user=payment.user,
            amount=payment.coin_received,
            reason="TOPUP",
        )
        return payment
