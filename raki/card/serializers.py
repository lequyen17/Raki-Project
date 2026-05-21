from rest_framework import serializers


class ReviewCardSerializer(serializers.Serializer):
    VALID_QUALITIES = ["again", "hard", "good", "easy"]

    quality = serializers.CharField()

    def validate_quality(self, value):
        quality = str(value).strip().lower()
        if quality not in self.VALID_QUALITIES:
            raise serializers.ValidationError("Invalid quality.")
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


class StudyCountsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    learning = serializers.IntegerField()
    review = serializers.IntegerField()
    total = serializers.IntegerField()
    today_completed_new = serializers.IntegerField()


class StudyOverallStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    new = serializers.IntegerField()
    learning = serializers.IntegerField()
    review = serializers.IntegerField()
    average_ease = serializers.FloatField()


class StudySessionResponseSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    counts = StudyCountsSerializer()
    overall_stats = StudyOverallStatsSerializer()
    results = StudyCardItemSerializer(many=True)
