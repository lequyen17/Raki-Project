from django.utils import timezone

from deck.models import Deck
from deck.repositories import EDIT_ROLES
from card.models import Card, Progress


class CardRepository:

    @staticmethod
    def get_cards_by_deck_ids(deck_ids):
        return (
            Card.objects.filter(note__deck_id__in=deck_ids)
            .select_related(
                "note",
                "template",
            )
            .prefetch_related("note__values__definition")
        )

    @staticmethod
    def get_cards_by_deck_ids_ordered(deck_ids):
        return (
            Card.objects.filter(note__deck_id__in=deck_ids)
            .select_related("note", "template")
            .prefetch_related("note__values__definition")
            .order_by("-id")
        )

    @staticmethod
    def get_progress_by_cards_and_user(cards, user):
        return Progress.objects.filter(
            card__in=cards,
            user=user,
        )

    @staticmethod
    def get_progress_dict(cards, user):
        return {
            p.card_id: p
            for p in Progress.objects.filter(
                card__in=cards,
                user=user,
            )
        }

    @staticmethod
    def count_started_new_today(deck_ids, user, today):
        return Progress.objects.filter(
            card__note__deck_id__in=deck_ids,
            user=user,
            created_at__date=today,
        ).count()

    @staticmethod
    def get_card_for_review(card_id, user):
        try:
            return Card.objects.filter(
                id=card_id,
                note__deck__deck_users__user=user,
            ).distinct().get()
        except Card.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_progress(user, card):
        return Progress.objects.get_or_create(
            user=user,
            card=card,
            defaults={
                "status": "learning",
                "repetition": 0,
                "interval": 1,
                "easiness": 2.5,
                "next_review": timezone.localdate(),
            },
        )

    @staticmethod
    def get_card_by_id(card_id, user):
        try:
            from django.db.models import Q
            return Card.objects.select_related("note", "template").prefetch_related("note__values__definition").filter(
                Q(id=card_id) & (Q(note__deck__deck_users__user=user) | Q(note__deck__share_mode="public"))
            ).distinct().get()
        except Card.DoesNotExist:
            return None

    @staticmethod
    def get_card_for_owner(card_id, user):
        try:
            return Card.objects.select_related("note", "template").prefetch_related("note__values__definition").filter(
                id=card_id,
                note__deck__deck_users__user=user,
                note__deck__deck_users__role="owner",
            ).distinct().get()
        except Card.DoesNotExist:
            return None

    @staticmethod
    def get_card_for_edit(card_id, user):
        try:
            return Card.objects.select_related("note", "template").prefetch_related("note__values__definition").filter(
                id=card_id,
                note__deck__deck_users__user=user,
                note__deck__deck_users__role__in=EDIT_ROLES,
            ).distinct().get()
        except Card.DoesNotExist:
            return None

    @staticmethod
    def delete_card(card_id, user):
        card = CardRepository.get_card_for_edit(card_id, user)
        if card:
            # Delete the note, which will cascade and delete all associated cards
            card.note.delete()
            return True
        return False
