from django.db import migrations


def assign_existing_data_to_owner(apps, schema_editor):
    User = apps.get_model("auth", "User")
    DailyEarning = apps.get_model("tracker", "DailyEarning")
    Expense = apps.get_model("tracker", "Expense")
    CoinCollection = apps.get_model("tracker", "CoinCollection")

    owner = User.objects.filter(username="isac12").first()

    if owner is None:
        raise RuntimeError(
            "System owner 'isac12' must exist before assigning "
            "existing business data."
        )

    DailyEarning.objects.filter(
        user__isnull=True
    ).update(user=owner)

    Expense.objects.filter(
        user__isnull=True
    ).update(user=owner)

    CoinCollection.objects.filter(
        user__isnull=True
    ).update(user=owner)


def reverse_assignment(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        (
            "tracker",
            "0013_coincollection_user_dailyearning_user_expense_user",
        ),
    ]

    operations = [
        migrations.RunPython(
            assign_existing_data_to_owner,
            reverse_assignment,
        ),
    ]
