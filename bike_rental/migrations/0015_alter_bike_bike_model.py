# Generated by Django 5.1 on 2024-09-10 10:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bike_rental", "0014_bike_owner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bike",
            name="bike_model",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="bikes",
                to="bike_rental.bikemodel",
            ),
        ),
    ]
