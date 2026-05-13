class LearningStrategy:

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
