from django.db import transaction

from apps.note.models import Note
from apps.note.models import FieldValue

from apps.note.services.card_service import (
    CardFactory,
)
from apps.note.services import card_service


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
                    definition.id,
                    "",
                )

                FieldValue.objects.create(
                    note=note,
                    definition=definition,
                    value=value,
                )

            service = card_service.CardService()

            # create cards
            templates = note_type.templates.all()

            created_cards = []

            for template in templates:

                cards = service.create_cards(
                    note,
                    template,
                    values_data,
                )

                created_cards.extend(cards)

            return {
                "note": note,
                "cards_created": len(created_cards),
            }
