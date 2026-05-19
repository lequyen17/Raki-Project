from rest_framework import serializers
import re
from .repositories import NoteRepository

FIELD_TAG_REGEX = r"\{\{[^}]+\}\}"
TYPE_TAG_REGEX = r"\{\{type:[^}]+\}\}"
CLOZE_REGEX = r"\{\{c(\d+)::.+?\}\}"


def extract_cloze_indexes(text):
    return [int(x) for x in re.findall(CLOZE_REGEX, text)]


def is_valid_cloze_sequence(indexes):
    if not indexes:
        return True
    unique_sorted = sorted(set(indexes))
    return unique_sorted == list(range(1, max(unique_sorted) + 1))


class NoteTypeSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_blank=True)
    definitions = serializers.ListField(child=serializers.CharField(allow_blank=True), required=False, default=[])
    templates = serializers.ListField(child=serializers.DictField(), required=False, default=[])

    def validate(self, attrs):
        name = self.initial_data.get("name")
        definitions_data = self.initial_data.get("definitions", [])
        templates_data = self.initial_data.get("templates", [])

        if not name:
            raise serializers.ValidationError("Name is required")

        if not definitions_data:
            raise serializers.ValidationError("At least one field is required")

        cleaned_definitions = []
        for d in definitions_data:
            field_name = str(d).strip()
            if not field_name:
                raise serializers.ValidationError("Field names cannot be empty")
            cleaned_definitions.append(field_name)

        if len(cleaned_definitions) != len(set(cleaned_definitions)):
            raise serializers.ValidationError("Field names must be unique")

        if not templates_data:
            raise serializers.ValidationError("At least one template is required")

        for template in templates_data:
            template_name = template.get("name", "").strip()
            is_cloze = template.get("is_cloze", False)
            front = template.get("front", "").strip()
            back = template.get("back", "").strip()

            if not template_name:
                raise serializers.ValidationError("Template name is required")

            if not front:
                raise serializers.ValidationError("Front design is required")

            if not is_cloze and not back:
                raise serializers.ValidationError("Back design is required")

            if not is_cloze:
                has_field_tag = re.search(FIELD_TAG_REGEX, front) or re.search(FIELD_TAG_REGEX, back)
                if not has_field_tag:
                    raise serializers.ValidationError("Normal templates must contain at least one field tag")

            if re.search(TYPE_TAG_REGEX, front):
                raise serializers.ValidationError("Type in answer fields can only be added to the Back design")

            if is_cloze:
                matches = re.findall(CLOZE_REGEX, front)
                if not matches:
                    raise serializers.ValidationError("Cloze templates must contain at least one {{c1::...}}")

                indexes = extract_cloze_indexes(front)
                if not is_valid_cloze_sequence(indexes):
                    raise serializers.ValidationError(f'Template "{template_name}" has invalid cloze numbers')

        attrs["name"] = name
        attrs["definitions_data"] = definitions_data
        attrs["templates_data"] = templates_data
        return attrs


class NoteCreateSerializer(serializers.Serializer):
    note_type_id = serializers.IntegerField(required=False)
    values = serializers.DictField(required=False, default={})

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        user = self.user
        note_type_id = self.initial_data.get("note_type_id")
        values_data = self.initial_data.get("values", {})

        if not note_type_id:
            raise serializers.ValidationError("note_type_id is required")

        note_type = NoteRepository.get_by_id_and_user(note_type_id, user)

        if not note_type:
            raise serializers.ValidationError("NoteType not found or not authorized", code="not_found")

        required_definition_ids = {str(d.id): d for d in note_type.definitions.all()}

        for def_id, definition in required_definition_ids.items():
            value = values_data.get(def_id)
            if value is None or not str(value).strip():
                raise serializers.ValidationError(f'Field "{definition.name}" is required')

        attrs["note_type"] = note_type
        attrs["values_data"] = values_data
        return attrs
