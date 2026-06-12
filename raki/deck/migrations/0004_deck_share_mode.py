from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deck", "0003_deck_coin_price"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="share_mode",
            field=models.CharField(
                choices=[
                    ("private", "Private"),
                    ("public", "Public"),
                    ("restricted", "Restricted"),
                ],
                default="private",
                max_length=20,
            ),
        ),
        migrations.RunSQL(
            sql="UPDATE deck_deck SET share_mode = 'public' WHERE is_public = TRUE;",
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
