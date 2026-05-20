from django.utils import timezone
from deck.repositories import DeckRepository
from card.repositories import CardRepository


class DeckService:

    @staticmethod
    def _get_deck_or_404(deck_id, user):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("Deck not found.")
        return deck

    # =========================
    # CREATE
    # =========================
    @staticmethod
    def create_deck(user, validated_data):
        deck = DeckRepository.create_user_deck(
            user=user,
            name=validated_data["name"],
            description=validated_data["description"],
        )
        return {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "parent_id": deck.parent_id,
            "created_at": deck.created_at,
        }

    # =========================
    # GET ALL USER DECKS
    # =========================
    @staticmethod
    def get_user_decks(user):
        decks = DeckRepository.get_user_decks(user)
        results = []
        for deck in decks:
            results.append(
                {
                    "id": deck.id,
                    "name": deck.name,
                    "description": deck.description or "",
                    "total_cards": deck.total_cards,
                    "parent_id": deck.parent_id,
                    "created_at": deck.created_at,
                }
            )
        return {
            "count": decks.count(),
            "results": results,
        }

    # =========================
    # GET DETAIL
    # =========================
    @staticmethod
    def get_deck_detail(deck_id, user):
        deck = DeckService._get_deck_or_404(deck_id, user)
        has_subdecks = DeckRepository.has_subdecks(deck, user)
        stats = DeckService.get_deck_stats(deck, user)
        return {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "is_leaf": not has_subdecks,
            "stats": stats,
        }

    # =========================
    # UPDATE
    # =========================
    @staticmethod
    def update_deck(deck, validated_data):
        deck = DeckRepository.update_deck(
            deck=deck,
            name=validated_data["name"],
            description=validated_data["description"],
        )
        return {
            "id": deck.id,
            "name": deck.name,
            "description": deck.description or "",
            "parent_id": deck.parent_id,
        }

    # =========================
    # MOVE (business rule nằm ở service)
    # =========================
    @staticmethod
    def move_deck(validated_data):
        deck = validated_data["deck"]
        parent = validated_data["parent"]
        DeckRepository.move_deck(deck, parent)
        return {
            "success": True,
            "deck_id": deck.id,
            "parent_id": deck.parent_id,
        }

    # =========================
    # DELETE
    # =========================
    @staticmethod
    def delete_deck(deck_id, user):
        deck = DeckService._get_deck_or_404(deck_id, user)
        DeckRepository.delete_deck(deck)
        return {"success": True}

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
