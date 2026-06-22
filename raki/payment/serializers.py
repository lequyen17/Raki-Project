from rest_framework import serializers


class WalletSummarySerializer(serializers.Serializer):
    coin_balance = serializers.IntegerField()


class CoinHistoryItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.IntegerField()
    reason = serializers.CharField()
    created_at = serializers.DateTimeField()


class CoinHistoryListResponseSerializer(serializers.Serializer):
    results = CoinHistoryItemSerializer(many=True)


class PaymentHistoryItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount_vnd = serializers.CharField()
    coin_received = serializers.IntegerField()
    status = serializers.CharField()
    created_at = serializers.DateTimeField()


class PaymentHistoryListResponseSerializer(serializers.Serializer):
    results = PaymentHistoryItemSerializer(many=True)


class VnpayTopupRequestSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=10000, help_text="Amount in VND, minimum 10,000")


class VnpayTopupResponseSerializer(serializers.Serializer):
    payUrl = serializers.CharField()
    paymentId = serializers.IntegerField()
    orderId = serializers.CharField()


class VnpayIpnResponseSerializer(serializers.Serializer):
    RspCode = serializers.CharField()
    Message = serializers.CharField()


class StripeTopupResponseSerializer(serializers.Serializer):
    sessionId = serializers.CharField()
    paymentId = serializers.IntegerField()
    orderId = serializers.CharField()
    payUrl = serializers.CharField()
