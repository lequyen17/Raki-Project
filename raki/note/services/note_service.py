from django.db import transaction

from note.models import Note
from note.models import FieldValue

from note.services.factories.card_factory import (
    CardFactory,
)


class NoteService:

    def create_note(
        self,
        deck,
        note_type,
        values_data,
    ):

        with transaction.atomic():

            note = Note.objects.create(
                note_type=note_type,
                deck=deck,
            )

            # create field values
            definitions = note_type.definitions.all()

            for definition in definitions:

                value = values_data.get(
                    str(definition.id),
                    "",
                )

                FieldValue.objects.create(
                    note=note,
                    definition=definition,
                    value=value,
                )

            # create cards
            templates = note_type.templates.all()

            card_factory = CardFactory()

            created_cards = []

            for template in templates:

                cards = card_factory.create_cards(
                    note,
                    template,
                    values_data,
                )

                created_cards.extend(cards)

            return {
                "note": note,
                "cards_created": len(created_cards),
            }
