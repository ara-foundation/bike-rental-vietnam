# Generated by Django 5.1 on 2024-08-31 13:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="AdditionalOption",
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
                (
                    "option_name",
                    models.CharField(default="Default Option", max_length=50),
                ),
                ("option_description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="FreeOfChargeService",
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
                (
                    "service_name",
                    models.CharField(default="Default Service", max_length=50),
                ),
                ("service_description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="Photo",
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
                ("image", models.ImageField(upload_to="tours/gallery/")),
                ("description", models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="TourDate",
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
                ("date", models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name="Tour",
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
                ("name", models.CharField(max_length=50)),
                ("tour_description", models.TextField()),
                ("duration", models.DurationField()),
                ("pick_up_time", models.TimeField()),
                ("cost", models.DecimalField(decimal_places=2, max_digits=10)),
                ("cost_options", models.TextField(blank=True, null=True)),
                (
                    "additional_options",
                    models.ManyToManyField(blank=True, to="tours.additionaloption"),
                ),
                (
                    "free_services",
                    models.ManyToManyField(blank=True, to="tours.freeofchargeservice"),
                ),
                (
                    "tour_photo_gallery",
                    models.ManyToManyField(blank=True, to="tours.photo"),
                ),
                (
                    "start_date",
                    models.ForeignKey(
                        blank=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tours.tourdate",
                    ),
                ),
            ],
        ),
    ]
