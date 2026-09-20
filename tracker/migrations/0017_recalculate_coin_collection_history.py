from django.db import migrations


def recalculate_coin_history(apps, schema_editor):
    CoinCollection = apps.get_model("tracker", "CoinCollection")

    collections = (
        CoinCollection.objects
        .all()
        .order_by("user_id", "collection_date", "created_at", "id")
    )

    previous_by_user = {}

    for collection in collections:
        previous = previous_by_user.get(collection.user_id)

        if previous is None:
            additional_coins = 0
            lost_coins = 0
        else:
            difference = (
                collection.coins_collected -
                previous.coins_collected
            )

            if difference > 0:
                additional_coins = difference
                lost_coins = 0
            elif difference < 0:
                additional_coins = 0
                lost_coins = abs(difference)
            else:
                additional_coins = 0
                lost_coins = 0

        CoinCollection.objects.filter(pk=collection.pk).update(
            additional_coins=additional_coins,
            lost_coins=lost_coins,
        )

        previous_by_user[collection.user_id] = collection


class Migration(migrations.Migration):

    dependencies = [
        ("tracker", "0016_coincollection_additional_coins_and_more"),
    ]

    operations = [
        migrations.RunPython(
            recalculate_coin_history,
            migrations.RunPython.noop,
        ),
    ]
