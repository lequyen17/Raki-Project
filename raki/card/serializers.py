from rest_framework import serializers

from card.repositories import CardRepository


class ReviewCardSerializer(serializers.Serializer):
    VALID_QUALITIES = ["again", "hard", "good", "easy"]

    quality = serializers.CharField()

    def validate_quality(self, value):
        quality = str(value).strip().lower()
        if quality not in self.VALID_QUALITIES:
            raise serializers.ValidationError("INVALID_QUALITY")
        return quality


# --- OpenAPI response schemas ---


class StudyCardTemplateSerializer(serializers.Serializer):
    front = serializers.CharField()
    back = serializers.CharField()


class CardDetailValueSerializer(serializers.Serializer):
    name = serializers.CharField(required=True, allow_blank=False)
    value = serializers.CharField(allow_blank=False, required=True)


class CardProgressItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    repetition = serializers.IntegerField()
    interval = serializers.IntegerField()
    easiness = serializers.FloatField()
    next_review = serializers.DateTimeField(allow_null=True)
    cloze_index = serializers.IntegerField(allow_null=True)
    template = StudyCardTemplateSerializer()
    field_values = CardDetailValueSerializer(many=True)
    is_owner = serializers.BooleanField(required=False)


class CardListResponseSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    deck_name = serializers.CharField()
    count = serializers.IntegerField()
    results = CardProgressItemSerializer(many=True)


class ReviewCardResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    interval = serializers.IntegerField()
    status = serializers.CharField()


class StudyCardItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
    cloze_index = serializers.IntegerField(allow_null=True)
    template = StudyCardTemplateSerializer()
    field_values = CardDetailValueSerializer(many=True)


class StudySessionResponseSerializer(serializers.Serializer):
    deck_name = serializers.CharField()
    results = StudyCardItemSerializer(many=True)


class CardDetailResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    cloze_index = serializers.IntegerField(allow_null=True)
    template = StudyCardTemplateSerializer()
    field_values = CardDetailValueSerializer(many=True)
    is_owner = serializers.BooleanField(required=False)


class CardUpdateSerializer(serializers.Serializer):
    field_values = CardDetailValueSerializer(many=True)

    def validate_field_values(self, value):
        card_id = self.context.get("card_id")
        user = self.context.get("user")
        
        if card_id and user:
            card = CardRepository.get_card_by_id(card_id, user)
            if not card:
                raise serializers.ValidationError("CARD_NOT_FOUND")
            
            valid_field_names = {fv.definition.name for fv in card.note.values.all()}
            for item in value:
                if item["name"] not in valid_field_names:
                    raise serializers.ValidationError(f"INVALID_FIELD_NAME: {item['name']}")
                    
        return value
