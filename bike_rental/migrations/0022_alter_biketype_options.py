# Generated by Django 5.1 on 2024-09-16 10:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bike_rental', '0021_alter_biketype_options_biketype_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='biketype',
            options={'ordering': ['-order']},
        ),
    ]
