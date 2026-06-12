from payment.models import CoinHistory, PaymentHistory


class WalletRepository:

    @staticmethod
    def get_coin_balance(user):
        try:
            return user.profile.coin_balance
        except AttributeError:
            return 0

    @staticmethod
    def get_coin_histories(user, filter_type="all"):
        queryset = CoinHistory.objects.filter(user=user)

        if filter_type == "deposit":
            queryset = queryset.filter(reason="TOPUP")
        elif filter_type == "spent":
            queryset = queryset.filter(reason="BUY_DECK")

        return queryset

    @staticmethod
    def get_payment_histories(user):
        return PaymentHistory.objects.filter(user=user)
