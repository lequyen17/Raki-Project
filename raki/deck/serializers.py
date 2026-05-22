from rest_framework import serializers

from .repositories import DeckRepository


class DeckSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100, allow_blank=True, required=False)
    description = serializers.CharField(
        required=False, allow_blank=True, allow_null=True
    )

    def validate(self, attrs):
        deck = self.context.get("deck")

        if deck:
            name = str(attrs.get("name", deck.name)).strip()
            description = str(attrs.get("description", deck.description or "")).strip()
        else:
            name = str(attrs.get("name", "")).strip()
            description = str(attrs.get("description", "")).strip()

        return {"name": name, "description": description}


class DeckMoveSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    parent_id = serializers.JSONField(required=False, allow_null=True)

    def validate(self, attrs):
        user = self.context["user"]
        deck_id = attrs.get("deck_id")
        parent_id = attrs.get("parent_id")

        deck = DeckRepository.get_deck_for_user(deck_id, user)

        if not deck:
            raise LookupError("Deck not found.")

        parent = DeckRepository.get_parent_deck_for_user(parent_id, user)

        if not parent:
            raise LookupError("Target parent deck not found.")

        if parent.id == deck.id:
            raise serializers.ValidationError("A deck cannot be moved into itself.")

        cursor = parent

        while cursor:
            if cursor.id == deck.id:
                raise serializers.ValidationError("Cannot move into its own subdeck.")
            cursor = cursor.parent

        return {"deck": deck, "parent": parent}


# --- OpenAPI response schemas ---


class DeckItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    parent_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField(required=False)


class DeckListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = DeckItemSerializer(many=True)


class DeckStatsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    learn = serializers.IntegerField()
    review = serializers.IntegerField()
    total = serializers.IntegerField()


class DeckMoveResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    deck_id = serializers.IntegerField()
    parent_id = serializers.IntegerField(allow_null=True)


class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class DeckDetailCountsSerializer(serializers.Serializer):
    new = serializers.IntegerField()
    learning = serializers.IntegerField()
    review = serializers.IntegerField()
    total = serializers.IntegerField()
    today_completed_new = serializers.IntegerField()


class DeckDetailOverallStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    new = serializers.IntegerField()
    learning = serializers.IntegerField()
    review = serializers.IntegerField()
    average_ease = serializers.FloatField()


class DeckDetailResponseSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField(allow_blank=True, allow_null=True)
    counts = DeckDetailCountsSerializer()
    overall_stats = DeckDetailOverallStatsSerializer()
