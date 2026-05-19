from django.utils import timezone
from deck.repositories import DeckRepository
from card.repositories import CardRepository


class DeckService:

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_deck(user, validated_data):
        return DeckRepository.create_user_deck(
            user=user,
            name=validated_data["name"],
            description=validated_data["description"],
        )

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_deck(deck, validated_data):
        return DeckRepository.update_deck(
            deck=deck,
            name=validated_data["name"],
            description=validated_data["description"],
        )

    # =========================
    # MOVE (business rule nằm ở service)
    # =========================
    @staticmethod
    def move_deck(deck, parent):

        if parent and parent.id == deck.id:
            raise ValueError("A deck cannot be moved into itself.")

        cursor = parent
        while cursor:
            if cursor.id == deck.id:
                raise ValueError("Cannot move into its own subdeck.")
            cursor = cursor.parent

        DeckRepository.move_deck(deck, parent)
        return deck

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_deck(deck):
        DeckRepository.delete_deck(deck)

    # =========================
    # DESCENDANTS TREE
    # =========================
    @staticmethod
    def get_descendant_ids(deck, user):

        def dfs(node):
            ids = [node.id]
            children = DeckRepository.get_child_decks(node, user)

            for child in children:
                ids.extend(dfs(child))

            return ids

        return dfs(deck)

    # =========================
    # STATS
    # =========================
    @staticmethod
    def get_deck_stats(deck, user):

        all_ids = DeckService.get_descendant_ids(deck, user)

        cards_qs = DeckRepository.get_cards_by_deck_ids(all_ids)
        progress_qs = CardRepository.get_progress_by_cards_and_user(cards_qs, user)

        total_cards = cards_qs.count()
        progress_count = progress_qs.count()

        now = timezone.now()

        new_count = (total_cards - progress_count) + progress_qs.filter(
            repetition=0
        ).count()

        learn_count = progress_qs.filter(
            repetition__gt=0,
            interval__lt=7,
        ).count()

        review_count = progress_qs.filter(
            interval__gte=7,
            next_review__lte=now,
        ).count()

        return {
            "new": new_count,
            "learn": learn_count,
            "review": review_count,
            "total": total_cards,
        }
