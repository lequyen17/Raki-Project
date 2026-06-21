from django.db import migrations, models


def copy_gross_coin_to_coin(apps, schema_editor):
    CoinTransaction = apps.get_model("payment", "CoinTransaction")
    for tx in CoinTransaction.objects.all():
        tx.coin = tx.gross_coin
        tx.save(update_fields=["coin"])


class Migration(migrations.Migration):

    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="cointransaction",
            name="coin",
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.RunPython(copy_gross_coin_to_coin, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="cointransaction",
            name="coin",
            field=models.PositiveIntegerField(),
        ),
        migrations.RemoveField(
            model_name="cointransaction",
            name="commission_coin",
        ),
        migrations.RemoveField(
            model_name="cointransaction",
            name="gross_coin",
        ),
        migrations.RemoveField(
            model_name="cointransaction",
            name="net_coin",
        ),
    ]
