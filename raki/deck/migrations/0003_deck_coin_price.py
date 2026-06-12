from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("deck", "0002_alter_userdeck_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="deck",
            name="coin_price",
            field=models.IntegerField(default=0),
        ),
    ]
