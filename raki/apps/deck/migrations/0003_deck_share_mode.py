from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deck", "0002_alter_userdeck_role"),
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
