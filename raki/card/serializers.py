class ReviewCardValidator:

    VALID_QUALITIES = [
        "again",
        "hard",
        "good",
        "easy",
    ]

    @staticmethod
    def validate(data):

        quality = str(data.get("quality", "")).strip().lower()

        if not quality:
            raise ValueError("Quality is required.")

        if quality not in ReviewCardValidator.VALID_QUALITIES:
            raise ValueError("Invalid quality.")

        return {
            "quality": quality,
        }
