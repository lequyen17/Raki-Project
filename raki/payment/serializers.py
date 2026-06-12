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
