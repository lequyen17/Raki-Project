from rest_framework import serializers

class ReviewCardSerializer(serializers.Serializer):
    quality = serializers.ChoiceField(
        choices=["again", "hard", "good", "easy"],
        error_messages={"invalid_choice": "Invalid quality."}
    )

    def validate_quality(self, value):
        if value not in ["again", "hard", "good", "easy"]:
            raise serializers.ValidationError("Invalid quality.")
        return value
