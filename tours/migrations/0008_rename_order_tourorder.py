# Generated by Django 5.1 on 2024-09-09 10:36

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("tours", "0007_order_author_alter_order_tour"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Order",
            new_name="TourOrder",
        ),
    ]
