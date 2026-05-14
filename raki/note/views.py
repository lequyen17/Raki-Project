from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import NoteType, FieldDefinition, Template, Note, FieldValue
from deck.models import Deck
from card.models import Card
from django.utils import timezone
from django.db.models import Q
from django.db import transaction

from note.services.note_service import NoteService
import re


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def note_types_view(request):

    if request.method == "POST":
        # Create a new NoteType
        name = request.data.get("name")
        definitions_data = request.data.get("definitions", [])
        templates_data = request.data.get("templates", [])

        if not name:
            return Response({"error": "Name is required"}, status=400)

        with transaction.atomic():
            note_type = NoteType.objects.create(name=name, user=request.user)
            for def_name in definitions_data:
                FieldDefinition.objects.create(note_type=note_type, name=def_name)
            for tmpl_data in templates_data:
                front_content = tmpl_data.get("front", "")
                if tmpl_data.get("is_cloze"):
                    front_content = f"<!--CLOZE_TEMPLATE-->\n{front_content}"

                Template.objects.create(
                    note_type=note_type,
                    name=tmpl_data.get("name", "Template"),
                    front=front_content,
                    back=tmpl_data.get("back", ""),
                )

        return Response({"success": True, "id": note_type.id}, status=201)

    # GET
    note_types = (
        NoteType.objects.filter(user__isnull=True)
        | NoteType.objects.filter(user=request.user)
    ).order_by("id")
    results = []
    for nt in note_types:
        defs = nt.definitions.all()
        tmpls = nt.templates.all()
        results.append(
            {
                "id": nt.id,
                "name": nt.name,
                "user_id": nt.user_id,
                "definitions": [{"id": d.id, "name": d.name} for d in defs],
                "templates": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "is_cloze": "<!--CLOZE_TEMPLATE-->" in t.front
                        or "{{cloze:" in t.front,
                        "front": t.front.replace("<!--CLOZE_TEMPLATE-->\n", "").replace(
                            "<!--CLOZE_TEMPLATE-->", ""
                        ),
                        "back": t.back,
                    }
                    for t in tmpls
                ],
            }
        )

    return Response({"results": results})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_note(request, deck_id):
    try:
        deck = Deck.objects.get(id=deck_id, deck_users__user=request.user)
    except Deck.DoesNotExist:
        return Response({"error": "Deck not found"}, status=404)

    note_type_id = request.data.get("note_type_id")
    values_data = request.data.get(
        "values", {}
    )  # Dict of definition_id -> value string

    if not note_type_id:
        return Response({"error": "note_type_id is required"}, status=400)

    try:
        note_type = NoteType.objects.get(id=note_type_id)
        if note_type.user_id is not None and note_type.user_id != request.user.id:
            return Response(
                {"error": "Not authorized to use this note type"}, status=403
            )
    except NoteType.DoesNotExist:
        return Response({"error": "NoteType not found"}, status=404)

    service = NoteService()

    result = service.create_note(
        deck=deck,
        note_type=note_type,
        values_data=values_data,
    )

    return Response(
        {
            "success": True,
            "note_id": result["note"].id,
            "cards_created": result["cards_created"],
        },
        status=201,
    )
