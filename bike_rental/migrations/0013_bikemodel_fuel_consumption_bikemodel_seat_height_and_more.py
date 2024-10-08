# Generated by Django 5.1 on 2024-09-09 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bike_rental', '0012_bikebrand_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='bikemodel',
            name='fuel_consumption',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bikemodel',
            name='seat_height',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bikemodel',
            name='weight',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
