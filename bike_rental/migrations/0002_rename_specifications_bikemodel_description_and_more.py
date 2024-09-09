# Generated by Django 5.1 on 2024-09-01 10:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bike_rental", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bikemodel",
            old_name="specifications",
            new_name="description",
        ),
        migrations.AddField(
            model_name="bikemodel",
            name="clearance",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bikemodel",
            name="fuel_system",
            field=models.CharField(default=5, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="bikemodel",
            name="gears",
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="bikemodel",
            name="displacement",
            field=models.FloatField(),
        ),
    ]
