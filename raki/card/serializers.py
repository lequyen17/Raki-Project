from rest_framework import serializers


class ReviewCardSerializer(serializers.Serializer):
    VALID_QUALITIES = ["again", "hard", "good", "easy"]

    quality = serializers.CharField()

    def validate_quality(self, value):
        quality = str(value).strip().lower()
        if quality not in self.VALID_QUALITIES:
            raise serializers.ValidationError(
                "INVALID_QUALITY"
            )
        return quality


# --- OpenAPI response schemas ---


class CardProgressItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    repetition = serializers.IntegerField()
    interval = serializers.IntegerField()
    easiness = serializers.FloatField()
    next_review = serializers.DateTimeField(allow_null=True)
    cloze_index = serializers.IntegerField(allow_null=True)


class CardListResponseSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    deck_name = serializers.CharField()
    count = serializers.IntegerField()
    results = CardProgressItemSerializer(many=True)


class ReviewCardResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    interval = serializers.IntegerField()
    status = serializers.CharField()


class StudyCardTemplateSerializer(serializers.Serializer):
    front = serializers.CharField()
    back = serializers.CharField()


class StudyCardItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    cloze_index = serializers.IntegerField(allow_null=True)
    template = StudyCardTemplateSerializer()
    field_values = serializers.DictField(child=serializers.CharField())


class StudySessionResponseSerializer(serializers.Serializer):
    deck_name = serializers.CharField()
    results = StudyCardItemSerializer(many=True)

