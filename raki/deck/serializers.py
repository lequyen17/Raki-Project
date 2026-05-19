from .repositories import DeckRepository


class DeckValidator:

    @staticmethod
    def validate(data, deck=None):

        if deck:
            name = str(data.get("name", deck.name)).strip()

            description = str(
                data.get(
                    "description",
                    deck.description or "",
                )
            ).strip()

        else:

            name = str(data.get("name", "")).strip()

            description = str(data.get("description", "")).strip()

        if not name:
            raise ValueError("Deck name is required.")

        if len(name) > 100:
            raise ValueError("Deck name must be at most 100 characters.")

        return {
            "name": name,
            "description": description,
        }


class DeckMoveValidator:

    @staticmethod
    def validate(data, user):

        deck_id = data.get("deck_id")
        parent_id = data.get("parent_id")

        if not deck_id:
            raise ValueError("deck_id is required.")

        deck = DeckRepository.get_deck_for_user(
            deck_id,
            user,
        )

        if not deck:
            raise LookupError("Deck not found.")

        parent = None

        if parent_id not in (
            None,
            "",
            "null",
        ):

            parent = DeckRepository.get_parent_deck_for_user(
                parent_id,
                user,
            )

            if not parent:
                raise LookupError("Target parent deck not found.")

            if parent.id == deck.id:
                raise ValueError("A deck cannot be moved into itself.")

            cursor = parent

            while cursor:

                if cursor.id == deck.id:
                    raise ValueError("Cannot move into its own subdeck.")

                cursor = cursor.parent

        return {
            "deck": deck,
            "parent": parent,
        }
