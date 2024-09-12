from django.db.models import Sum

from bike_rental.models import Bike


def get_total_bikes_for_brand(brand_name):
    total_bikes = Bike.objects.filter(bike_model__brand__name=brand_name).aggregate(
        total=Sum("amount")
    )["total"]
    return total_bikes or 0  # Return 0 if no bikes are found
