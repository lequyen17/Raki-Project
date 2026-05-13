import re

from card.models import Card


class ClozeCardFactory:

    def get_max_cloze(self, template, values_data):

        max_cloze = 0

        # check field values
        for val_text in values_data.values():

            matches = re.findall(r"\{\{c(\d+)::", val_text)

            for m in matches:

                idx = int(m)

                if idx > max_cloze:
                    max_cloze = idx

        # check template itself
        template_matches = re.findall(
            r"\{\{c(\d+)::",
            template.front,
        )

        for m in template_matches:

            idx = int(m)

            if idx > max_cloze:
                max_cloze = idx

        return max_cloze

    def create_cards(self, note, template, values_data):

        max_cloze = self.get_max_cloze(
            template,
            values_data,
        )

        cards = []

        # nếu không có cloze
        if max_cloze == 0:

            card = Card.objects.create(
                note=note,
                template=template,
                cloze_index=0,
            )

            cards.append(card)

            return cards

        # tạo nhiều cards theo cloze index
        for i in range(1, max_cloze + 1):

            card = Card.objects.create(
                note=note,
                template=template,
                cloze_index=i,
            )

            cards.append(card)

        return cards
