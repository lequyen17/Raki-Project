from payment.repositories import WalletRepository


class WalletService:

    @staticmethod
    def get_wallet_summary(user):
        return {
            "coin_balance": WalletRepository.get_coin_balance(user),
        }

    @staticmethod
    def get_coin_histories(user):
        histories = WalletRepository.get_coin_histories(user)
        return {
            "results": [
                {
                    "id": item.id,
                    "amount": item.amount,
                    "reason": item.reason,
                    "created_at": item.created_at,
                }
                for item in histories
            ]
        }

    @staticmethod
    def get_payment_histories(user):
        payments = WalletRepository.get_payment_histories(user)
        return {
            "results": [
                {
                    "id": item.id,
                    "amount_vnd": str(item.amount_vnd),
                    "coin_received": item.coin_received,
                    "status": item.status,
                    "created_at": item.created_at,
                }
                for item in payments
            ]
        }
