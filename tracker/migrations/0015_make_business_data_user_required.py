from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "tracker",
            "0014_assign_existing_data_to_owner",
        ),
    ]

    operations = [
        migrations.AlterField(
            model_name="dailyearning",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="daily_earnings",
                to="auth.user",
            ),
        ),
        migrations.AlterField(
            model_name="expense",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="expenses",
                to="auth.user",
            ),
        ),
        migrations.AlterField(
            model_name="coincollection",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="coin_collections",
                to="auth.user",
            ),
        ),
    ]
