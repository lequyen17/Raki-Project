from datetime import timedelta
from django.utils import timezone

from card.services.strategies.learning_strategy import LearningStrategy
from card.services.strategies.sm2_strategy import SM2ReviewStrategy


class ReviewService:

    def __init__(self):

        self.learning_strategy = LearningStrategy()
        self.review_strategy = SM2ReviewStrategy()

    def review_card(self, progress, quality):

        if progress.status == "learning":

            updated_progress = self.learning_strategy.review(progress, quality)

        else:

            updated_progress = self.review_strategy.review(progress, quality)

        updated_progress.next_review = timezone.localdate() + timedelta(
            days=updated_progress.interval
        )

        updated_progress.save()

        return updated_progress
