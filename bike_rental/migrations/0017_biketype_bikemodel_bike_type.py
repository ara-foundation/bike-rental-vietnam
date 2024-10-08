# Generated by Django 5.1 on 2024-09-16 01:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bike_rental', '0016_merge_20240913_0904'),
    ]

    operations = [
        migrations.CreateModel(
            name='BikeType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100, unique=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='bike_type_images/')),
            ],
        ),
        migrations.AddField(
            model_name='bikemodel',
            name='bike_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bike_models', to='bike_rental.biketype'),
        ),
    ]
