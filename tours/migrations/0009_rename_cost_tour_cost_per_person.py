# Generated by Django 5.1 on 2024-09-11 08:29

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tours", "0008_rename_order_tourorder"),
    ]

    operations = [
        migrations.RenameField(
            model_name="tour",
            old_name="cost",
            new_name="cost_per_person",
        ),
    ]
