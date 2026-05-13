class SM2ReviewStrategy:

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
