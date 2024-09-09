# Generated by Django 5.1 on 2024-09-01 11:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bike_rental", "0003_remove_bikemodel_fuel_system"),
    ]

    operations = [
        migrations.AddField(
            model_name="bikemodel",
            name="fuel_system",
            field=models.CharField(default="carburettor", max_length=255),
        ),
        migrations.AddField(
            model_name="bikemodel",
            name="tank",
            field=models.FloatField(default=0),
        ),
    ]
