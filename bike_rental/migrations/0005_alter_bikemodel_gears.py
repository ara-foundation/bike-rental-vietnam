# Generated by Django 5.1 on 2024-09-01 11:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bike_rental", "0004_bikemodel_fuel_system_bikemodel_tank"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bikemodel",
            name="gears",
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
