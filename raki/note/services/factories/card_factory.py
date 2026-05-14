from note.services.factories.normal_card_factory import (
    NormalCardFactory,
)

from note.services.factories.cloze_card_factory import (
    ClozeCardFactory,
)


class CardFactory:

    def create_cards(
        self,
        note,
        template,
        values_data,
    ):

        is_cloze_template = "<!--CLOZE_TEMPLATE-->" in template.front

        if is_cloze_template:

            factory = ClozeCardFactory()

        else:

            factory = NormalCardFactory()

        return factory.create_cards(
            note,
            template,
            values_data,
        )
