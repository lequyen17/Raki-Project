from django.apps import AppConfig


class PaymentInfrastructureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "infrastructure.payment"
    label = "infrastructure_payment"

    def ready(self):
        from apps.payment.registry import PaymentGatewayRegistry
        from infrastructure.payment.vnpay_gateway import VNPayGateway
        from infrastructure.payment.momo_gateway import MomoGateway
        from infrastructure.payment.stripe_gateway import StripeGateway

        # Register VNPay
        PaymentGatewayRegistry.register(
            "vnpay",
            VNPayGateway(
                tmn_code="DZLOX1ST",
                secret_key="FRD8HSODHRZU3MUSVYOE0O14J48Z190J",
                payment_url="https://sandbox.vnpayment.vn/paymentv2/vpcpay.html",
            ),
        )

        # Register Momo
        PaymentGatewayRegistry.register(
            "momo",
            MomoGateway(
                partner_code="MOMO",
                access_key="F8BBA842ECF85",
                secret_key="K951B6PE1waDMi640xX08PD3vg6EkVlz",
                endpoint="https://test-payment.momo.vn/v2/gateway/api/create",
            ),
        )

        # Register Stripe
        PaymentGatewayRegistry.register(
            "stripe",
            StripeGateway(
                secret_key="sk_test_51TkpnARuDgugaDRen1N64IetOEcfhioMyHcbIZfVHjmHbP64mhkriEApk1bMiBWn1RvCNlF43Z4KiZmWl5qBxT0Z00gRqfMhIe",
                webhook_secret="whsec_jeYVUSC8RMR865OWOiWmqSKTVF6UZWnU",
            ),
        )
