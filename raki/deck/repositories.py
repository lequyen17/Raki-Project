from django.db.models import Count
from django.utils import timezone

from deck.models import Deck, UserDeck
from card.models import Card, Progress


class DeckRepository:

    @staticmethod
    def get_user_decks(user):
        return (
            Deck.objects.filter(deck_users__user=user)
            .annotate(total_cards=Count("notes__cards"))
            .order_by("name")
        )

    @staticmethod
    def create_user_deck(user, name, description=""):
        deck = Deck.objects.create(
            name=name,
            description=description,
            parent=None,
        )

        UserDeck.objects.create(
            user=user,
            deck=deck,
            role="owner",
        )

        return deck

    @staticmethod
    def get_deck_for_user(deck_id, user):
        try:
            return Deck.objects.get(
                id=deck_id,
                deck_users__user=user,
            )
        except Deck.DoesNotExist:
            return None

    @staticmethod
    def get_parent_deck_for_user(parent_id, user):
        try:
            return Deck.objects.get(
                id=parent_id,
                deck_users__user=user,
            )
        except Deck.DoesNotExist:
            return None

    @staticmethod
    def update_deck(deck, name, description):
        deck.name = name
        deck.description = description

        deck.save(
            update_fields=[
                "name",
                "description",
            ]
        )

        return deck

    @staticmethod
    def move_deck(deck, parent):
        deck.parent = parent
        deck.save(update_fields=["parent"])

        return deck

    @staticmethod
    def delete_deck(deck):
        deck.delete()

    @staticmethod
    def has_subdecks(deck, user):
        return Deck.objects.filter(
            parent=deck,
            deck_users__user=user,
        ).exists()

    @staticmethod
    def get_child_decks(deck, user):
        return Deck.objects.filter(
            parent=deck,
            deck_users__user=user,
        )

    @staticmethod
    def get_cards_by_deck_ids(deck_ids):
        return Card.objects.filter(note__deck_id__in=deck_ids)
