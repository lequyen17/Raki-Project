from rest_framework import serializers
from .repositories import DeckRepository

class DeckSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)

    def __init__(self, *args, **kwargs):
        self.deck = kwargs.pop('deck', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if self.deck:
            name = str(attrs.get("name", self.deck.name)).strip()
            description = str(attrs.get("description", self.deck.description or "")).strip()
        else:
            name = str(attrs.get("name", "")).strip()
            description = str(attrs.get("description", "")).strip()

        if not name:
            raise serializers.ValidationError("Deck name is required.")

        if len(name) > 100:
            raise serializers.ValidationError("Deck name must be at most 100 characters.")

        attrs["name"] = name
        attrs["description"] = description
        return attrs


class DeckMoveSerializer(serializers.Serializer):
    deck_id = serializers.IntegerField(required=False)
    parent_id = serializers.IntegerField(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        user = self.user
        deck_id = self.initial_data.get("deck_id")
        parent_id = self.initial_data.get("parent_id")

        if not deck_id:
            raise serializers.ValidationError("deck_id is required.")

        deck = DeckRepository.get_deck_for_user(deck_id, user)

        if not deck:
            raise serializers.ValidationError("Deck not found.", code="not_found")

        parent = None

        if parent_id not in (None, "", "null"):
            parent = DeckRepository.get_parent_deck_for_user(parent_id, user)

            if not parent:
                raise serializers.ValidationError("Target parent deck not found.", code="not_found")

            if parent.id == deck.id:
                raise serializers.ValidationError("A deck cannot be moved into itself.")

            cursor = parent
            while cursor:
                if cursor.id == deck.id:
                    raise serializers.ValidationError("Cannot move into its own subdeck.")
                cursor = cursor.parent

        attrs["deck"] = deck
        attrs["parent"] = parent
        return attrs
