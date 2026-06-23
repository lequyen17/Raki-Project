from datetime import timedelta
from django.utils import timezone


from abc import ABC, abstractmethod


class ReviewStrategy(ABC):
    @abstractmethod
    def review(self, progress, quality):
        pass


class LearningStrategy(ReviewStrategy):
    def review(self, p, quality):

        p.interval = 0

        if quality == "again":
            p.repetition = 0
            p.status = "learning"

        elif quality == "hard":
            p.repetition = 0

        elif quality == "good":
            p.repetition += 1

            if p.repetition >= 2:
                p.status = "review"
                p.repetition = 0
                p.interval = 1

        elif quality == "easy":
            p.status = "review"
            p.repetition = 0
            p.interval = 1

        return p


class SM2ReviewStrategy(ReviewStrategy):

    def review(self, p, quality):

        E = p.easiness

        if quality == "again":
            q = 0
            p.repetition = 0
            p.interval = 0
            p.status = "learning"

        elif quality == "hard":
            q = 3
            p.repetition = 0
            p.interval = max(1, int(p.interval * 1.2))

        elif quality == "good":
            q = 4

            if p.repetition == 0:
                p.interval = 1

            elif p.repetition == 1:
                p.interval = 6

            else:
                p.interval = max(1, int(p.interval * E))

            p.repetition += 1

        elif quality == "easy":
            q = 5

            if p.repetition == 0:
                p.interval = 4

            else:
                p.interval = max(1, int(p.interval * E * 1.3))

            p.repetition += 1

        p.easiness = max(1.3, E + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02)))

        return p


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
