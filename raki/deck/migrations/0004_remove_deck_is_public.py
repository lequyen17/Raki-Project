from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("deck", "0003_deck_share_mode"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="deck",
            name="is_public",
        ),
    ]
