# Generated by Django 5.1 on 2024-09-10 18:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bike_rental', '0014_bikemodel_max_speed'),
    ]

    operations = [
        migrations.RenameField(
            model_name='bikemodel',
            old_name='clearance',
            new_name='wheel_size',
        ),
    ]
