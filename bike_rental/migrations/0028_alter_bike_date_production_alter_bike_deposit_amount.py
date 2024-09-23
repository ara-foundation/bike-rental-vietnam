# Generated by Django 5.1 on 2024-09-21 21:36

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bike_rental', '0027_rename_owner_bike_bike_provider_and_more'),
    ]

    operations = [
               migrations.AlterField(
            model_name='bike',
            name='date_production',
            field=models.DateField(default=datetime.date(2015, 1, 1)),
        ),

        migrations.AlterField(
            model_name='bike',
            name='deposit_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
