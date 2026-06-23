from abc import ABC, abstractmethod
from typing import Dict, Any

class PaymentGatewayInterface(ABC):
    @abstractmethod
    def create_payment(self, amount: int, order_id: str, **kwargs) -> Dict[str, Any]:
        """
        Create a payment request.
        Returns a dictionary containing at least 'pay_url' or other relevant data.
        """
        pass

    @abstractmethod
    def verify_payment(self, request_data: Any) -> bool:
        """
        Verify a payment callback/IPN/webhook.
        Returns True if the request is authentic.
        """
        pass
