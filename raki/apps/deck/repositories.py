from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from apps.deck.models import Deck, UserDeck
from apps.card.models import Card, Progress

User = get_user_model()

EDIT_ROLES = ("owner", "editor")


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
            return (
                Deck.objects.filter(Q(deck_users__user=user) | Q(share_mode="public"))
                .distinct()
                .get(id=deck_id)
            )
        except Deck.DoesNotExist:
            return None

    @staticmethod
    def get_deck_for_owner(deck_id, user):
        try:
            return Deck.objects.get(
                id=deck_id,
                deck_users__user=user,
                deck_users__role="owner",
            )
        except Deck.DoesNotExist:
            return None

    @staticmethod
    def get_deck_for_edit(deck_id, user):
        try:
            return Deck.objects.get(
                id=deck_id,
                deck_users__user=user,
                deck_users__role__in=EDIT_ROLES,
            )
        except Deck.DoesNotExist:
            return None

    @staticmethod
    def get_public_decks():
        return Deck.objects.filter(share_mode="public").order_by("-created_at")

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
    def update_deck(deck, name, description, coin_price=None):
        deck.name = name
        deck.description = description
        if coin_price is not None:
            deck.coin_price = coin_price

        update_fields = ["name", "description"]
        if coin_price is not None:
            update_fields.append("coin_price")

        deck.save(update_fields=update_fields)

        return deck

    @staticmethod
    def update_deck_share(deck, share_mode, coin_price):
        deck.share_mode = share_mode
        deck.coin_price = coin_price
        deck.save(update_fields=["share_mode", "coin_price"])
        return deck

    @staticmethod
    def get_collaborators(deck):
        return (
            UserDeck.objects.filter(deck=deck)
            .exclude(role="owner")
            .select_related("user")
        )

    @staticmethod
    def remove_non_owner_members(deck):
        UserDeck.objects.filter(deck=deck).exclude(role="owner").delete()

    @staticmethod
    def get_all_descendants(deck):
        descendants = [deck]
        for child in Deck.objects.filter(parent=deck):
            descendants.extend(DeckRepository.get_all_descendants(child))
        return descendants

    @staticmethod
    def search_users(query, exclude_user, limit=8):
        return (
            User.objects.filter(username__icontains=query)
            .exclude(id=exclude_user.id)
            .order_by("username")[:limit]
        )

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
        if deck.share_mode == "public":
            return Deck.objects.filter(parent=deck).exists()
        return Deck.objects.filter(
            parent=deck,
            deck_users__user=user,
        ).exists()

    @staticmethod
    def get_child_decks(deck, user):
        if deck.share_mode == "public":
            return Deck.objects.filter(parent=deck)
        return Deck.objects.filter(
            parent=deck,
            deck_users__user=user,
        )

    @staticmethod
    def get_cards_by_deck_ids(deck_ids):
        return Card.objects.filter(note__deck_id__in=deck_ids)
