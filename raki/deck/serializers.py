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
            raise LookupError("DECK_NOT_FOUND")

        if parent_id is None:
            return {"deck": deck, "parent": None}

        parent = DeckRepository.get_parent_deck_for_user(parent_id, user)

        if not parent:
            raise LookupError("PARENT_DECK_NOT_FOUND")

        if parent.id == deck.id:
            raise serializers.ValidationError("DECK_MOVE_SELF")

        cursor = parent

        while cursor:
            if cursor.id == deck.id:
                raise serializers.ValidationError("DECK_MOVE_SUBDECK")
            cursor = cursor.parent

        return {"deck": deck, "parent": parent}


# --- OpenAPI response schemas ---


class DeckItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    description = serializers.CharField()
    parent_id = serializers.IntegerField(allow_null=True)
    created_at = serializers.DateTimeField(required=False)
    share_mode = serializers.CharField(required=False)
    coin_price = serializers.IntegerField(required=False)
    role = serializers.CharField(required=False)


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
    coin_price = serializers.IntegerField(required=False)
    share_mode = serializers.CharField(required=False)
    role = serializers.CharField(required=False)
    counts = DeckDetailCountsSerializer()
    overall_stats = DeckDetailOverallStatsSerializer()

class PublicDeckItemSerializer(DeckItemSerializer):
    owner = serializers.CharField()

class PublicDeckListResponseSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = PublicDeckItemSerializer(many=True)


class DeckCollaboratorSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    role = serializers.CharField()


class DeckShareSettingsSerializer(serializers.Serializer):
    share_mode = serializers.ChoiceField(choices=["private", "public", "restricted"])
    coin_price = serializers.IntegerField(min_value=0, required=False, default=0)

    def validate(self, attrs):
        share_mode = attrs["share_mode"]
        coin_price = attrs.get("coin_price", 0)

        if share_mode == "public" and coin_price < 0:
            raise serializers.ValidationError("INVALID_COIN_PRICE")

        if share_mode != "public":
            attrs["coin_price"] = 0

        return attrs


class DeckCollaboratorAddSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    role = serializers.ChoiceField(choices=["viewer", "editor"])

    def validate_username(self, value):
        username = value.strip()
        if not username:
            raise serializers.ValidationError("USERNAME_REQUIRED")
        return username


class DeckShareSettingsResponseSerializer(serializers.Serializer):
    share_mode = serializers.CharField()
    coin_price = serializers.IntegerField()
    access_type = serializers.CharField()
    collaborators = DeckCollaboratorSerializer(many=True)


class UserSearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class UserSearchResponseSerializer(serializers.Serializer):
    results = UserSearchResultSerializer(many=True)
