from deck.repositories import DeckRepository
from note.repositories import NoteRepository
from note.serializers import NoteTypeValidator, NoteCreateValidator
from note.services.note_service import NoteService

class NoteMainService:
    @staticmethod
    def create_note_type(user, request_data):
        validated_data = NoteTypeValidator.validate(request_data)
        name = validated_data["name"]
        definitions_data = validated_data["definitions_data"]
        templates_data = validated_data["templates_data"]
        
        note_type = NoteRepository.create_note_type_with_relations(
            user=user,
            name=name,
            definitions_data=definitions_data,
            templates_data=templates_data,
        )
        return {
            "success": True,
            "id": note_type.id,
        }

    @staticmethod
    def get_note_types(user):
        note_types = NoteRepository.get_all_visible_for_user(user)
        results = []
        for nt in note_types:
            results.append(
                {
                    "id": nt.id,
                    "name": nt.name,
                    "user_id": nt.user_id,
                    "definitions": [
                        {
                            "id": d.id,
                            "name": d.name,
                        }
                        for d in nt.definitions.all()
                    ],
                    "templates": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "is_cloze": "<!--CLOZE_TEMPLATE-->" in t.front,
                            "front": t.front.replace("<!--CLOZE_TEMPLATE-->", ""),
                            "back": t.back,
                        }
                        for t in nt.templates.all()
                    ],
                }
            )
        return {"results": results}

    @staticmethod
    def create_note(deck_id, user, request_data):
        deck = DeckRepository.get_deck_for_user(deck_id, user)
        if not deck:
            raise LookupError("Deck not found")

        validated_data = NoteCreateValidator.validate(request_data, user)
        note_type = validated_data["note_type"]
        values_data = validated_data["values_data"]

        service = NoteService()
        result = service.create_note(
            deck=deck,
            note_type=note_type,
            values_data=values_data,
        )
        return {
            "success": True,
            "note_id": result["note"].id,
            "cards_created": result["cards_created"],
        }
