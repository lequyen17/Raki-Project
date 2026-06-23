from apps.payment.models import CoinHistory, PaymentHistory


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
        return PaymentHistory.objects.filter(user=user)
