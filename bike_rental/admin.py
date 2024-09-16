from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin

from .models import Bike, BikeBrand, BikeModel, BikeOrder, Client, BikeType


class BikeBrandAdmin(ImportExportModelAdmin):
    list_display = ["name", "logo_preview"]
    readonly_fields = ["logo_preview"]

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" height="100" />')
        return "No logo"

    logo_preview.short_description = "Logo preview"


class BikeModelAdmin(ImportExportModelAdmin):
    list_display = ["brand", "model", "transmission"]
    list_filter = ["brand", "transmission"]
    search_fields = ["model", "brand__name"]
    fields = [
        "brand",
        "model",
        "transmission",
        "gears",
        "displacement",
        "fuel_system",
        "tank",
        "wheel_size",
        "description",
        "bike_model_photo",
        "bike_type",
    ]


@admin.register(Bike)
class BikeAdmin(ImportExportModelAdmin):
    list_display = ["bike_model", "amount", "price_per_day", "availability", "owner"]
    list_filter = ["availability", "bike_model__brand", "owner"]
    search_fields = ["bike_model__brand__name", "bike_model__model"]
    readonly_fields = ["photo_preview"]
    exclude = ("owner",)

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)

        # Check if the user is part of the "Bike Owner" group
        if request.user.groups.filter(name="Bike Owner").exists():
            # Filter bikes to show only those related to owner
            return qs.filter(owner=request.user)

        # For superusers, return all bikes
        if request.user.is_superuser:
            return qs

        # In all other cases (if a user is not in any group), return an empty queryset
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change or obj.owner is None:
            # Automatically set the owner to the
            # logged-in user if this is a new object or if owner is not set
            obj.owner = request.user
        super().save_model(request, obj, form, change)

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="150" height="150" />')
        return "No photo"

    photo_preview.short_description = "Photo preview"


class ClientAdmin(ImportExportModelAdmin):
    pass  # Если нет дополнительных настроек, используйте pass


class OrderAdmin(ImportExportModelAdmin):
    pass  # Если нет дополнительных настроек, используйте pass


# Register your models here.
admin.site.register(BikeModel, BikeModelAdmin)
admin.site.register(BikeBrand, BikeBrandAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(BikeOrder, OrderAdmin)
admin.site.register(BikeType)
