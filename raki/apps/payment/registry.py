class PaymentGatewayRegistry:
    _gateways = {}

    @classmethod
    def register(cls, name: str, gateway_instance):
        """Register a gateway implementation"""
        cls._gateways[name] = gateway_instance

    @classmethod
    def get(cls, name: str):
        """Get a gateway implementation by name"""
        gateway = cls._gateways.get(name)
        if not gateway:
            raise ValueError(f"Payment gateway '{name}' is not registered.")
        return gateway
