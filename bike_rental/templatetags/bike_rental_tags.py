from django import template
from bike_rental.models import BikeBrand

register = template.Library()

@register.filter
def get_brand_name(brand_id):
    try:
        return BikeBrand.objects.get(id=brand_id).name
    except BikeBrand.DoesNotExist:
        return "Unknown Brand"
