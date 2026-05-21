import re

from rest_framework import serializers

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


class NoteTemplateSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=True)
    is_cloze = serializers.BooleanField(required=False, default=False)
    front = serializers.CharField(allow_blank=True, required=False, default="")
    back = serializers.CharField(allow_blank=True, required=False, default="")


class NoteTypeSerializer(serializers.Serializer):
    name = serializers.CharField()
    definitions = serializers.ListField(
        child=serializers.CharField(),
        help_text="List of field names, e.g. ['Front', 'Back']",
    )
    templates = NoteTemplateSerializer(many=True)

    def validate(self, attrs):
        name = attrs.get("name")
        definitions_data = attrs.get("definitions", [])
        templates_data = attrs.get("templates", [])

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
                has_field_tag = re.search(FIELD_TAG_REGEX, front) or re.search(
                    FIELD_TAG_REGEX, back
                )

                if not has_field_tag:
                    raise serializers.ValidationError(
                        "Normal templates must contain at least one field tag"
                    )

            if re.search(TYPE_TAG_REGEX, front):
                raise serializers.ValidationError(
                    "Type in answer fields can only be added to the Back design"
                )

            if is_cloze:
                matches = re.findall(CLOZE_REGEX, front)

                if not matches:
                    raise serializers.ValidationError(
                        "Cloze templates must contain at least one {{c1::...}}"
                    )

                indexes = extract_cloze_indexes(front)

                if not is_valid_cloze_sequence(indexes):
                    raise serializers.ValidationError(
                        f'Template "{template_name}" has invalid cloze numbers'
                    )

        return {
            "name": name,
            "definitions_data": definitions_data,
            "templates_data": templates_data,
        }


class NoteCreateSerializer(serializers.Serializer):
    note_type_id = serializers.IntegerField()
    values = serializers.DictField(
        child=serializers.CharField(allow_blank=True),
        help_text="Map definition id (string) -> field value",
    )

    def validate(self, attrs):
        user = self.context["user"]
        note_type_id = attrs.get("note_type_id")
        values_data = attrs.get("values", {})

        note_type = NoteRepository.get_by_id_and_user(note_type_id, user)

        if not note_type:
            raise LookupError("NoteType not found or not authorized")

        required_definitions = {str(d.id): d for d in note_type.definitions.all()}

        for def_id, definition in required_definitions.items():
            value = values_data.get(def_id)

            if value is None or not str(value).strip():
                raise serializers.ValidationError(
                    f'Field "{definition.name}" is required'
                )

        return {"note_type": note_type, "values_data": values_data}


# --- OpenAPI response schemas ---


class NoteTypeDefinitionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class NoteTypeTemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    is_cloze = serializers.BooleanField()
    front = serializers.CharField()
    back = serializers.CharField()


class NoteTypeItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    user_id = serializers.IntegerField(allow_null=True)
    definitions = NoteTypeDefinitionSerializer(many=True)
    templates = NoteTypeTemplateSerializer(many=True)


class NoteTypeListResponseSerializer(serializers.Serializer):
    results = NoteTypeItemSerializer(many=True)


class NoteTypeCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    id = serializers.IntegerField()


class NoteCreateResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    note_id = serializers.IntegerField()
    cards_created = serializers.IntegerField()
