# Generated by Django 5.1 on 2024-08-31 22:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BikeBrand",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="BikeModel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("model", models.CharField(max_length=255)),
                ("transmission", models.CharField(max_length=255)),
                ("displacement", models.IntegerField()),
                ("specifications", models.TextField()),
                (
                    "brand",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="models",
                        to="bike_rental.bikebrand",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Bike",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("deposit_amount", models.IntegerField()),
                ("amount", models.IntegerField()),
                ("availability", models.BooleanField(default=True)),
                (
                    "photos",
                    models.ImageField(blank=True, null=True, upload_to="images/"),
                ),
                ("description", models.TextField()),
                (
                    "bike_model",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="bikes",
                        to="bike_rental.bikemodel",
                    ),
                ),
            ],
        ),
    ]
