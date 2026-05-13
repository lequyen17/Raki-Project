from card.models import Card


class NormalCardFactory:

    def create_cards(self, note, template, values_data=None):

        card = Card.objects.create(
            note=note,
            template=template,
            cloze_index=0,
        )

        return [card]
