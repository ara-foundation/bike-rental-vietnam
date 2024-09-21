from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import Bike, BikeBrand, BikeModel, BikeOrder, Client, BikeType, RidePurpose, BikeProvider, ProviderService, Price
from .resources import BikeModelResource, BikeResource, PriceResource

class BikeBrandAdmin(ImportExportModelAdmin):
    list_display = ["name", "logo_preview"]
    readonly_fields = ["logo_preview"]

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" height="100" />')
        return "No logo"

    logo_preview.short_description = "Logo preview"

class BikeModelAdmin(ImportExportModelAdmin):
    resource_class = BikeModelResource
    list_display = ["brand", "model", "transmission", "displacement", "bike_type"]
    list_filter = ["brand", "transmission", "bike_type", "ride_purposes"]
    search_fields = ["model", "brand__name"]
    filter_horizontal = ['ride_purposes']

class PriceInline(admin.TabularInline):
    model = Price
    extra = 1

@admin.register(Bike)
class BikeAdmin(ImportExportModelAdmin):
    resource_class = BikeResource
    list_display = ["bike_model", "amount", "get_price", "availability", "bike_provider"]
    list_filter = ["availability", "bike_model__brand", "bike_provider"]
    search_fields = ["bike_model__brand__name", "bike_model__model"]
    readonly_fields = ["photo_preview"]
    inlines = [PriceInline]

    def get_price(self, obj):
        price = obj.prices.first()
        return price.day1_price if price else "N/A"
    get_price.short_description = "Price (1 day)"

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)

        # Check if the user is part of the "Bike bike_provider" group
        if request.user.groups.filter(name="Bike Provider").exists():
            # Filter bikes to show only those related to bike_provider
            return qs.filter(bike_provider=request.user)

        # For superusers, return all bikes
        if request.user.is_superuser:
            return qs

        # In all other cases (if a user is not in any group), return an empty queryset
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change or obj.bike_provider is None:
            # Automatically set the bike_provider to the
            # logged-in user if this is a new object or if bike_provider is not set
            obj.bike_provider = request.user
        super().save_model(request, obj, form, change)

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="150" height="150" />')
        return "No photo"

    photo_preview.short_description = "Photo preview"


class ClientAdmin(ImportExportModelAdmin):
    list_display = ['name', 'contact']
    search_fields = ['name', 'contact']

class BikeOrderAdmin(ImportExportModelAdmin):
    list_display = ['client', 'bike', 'start_date', 'duration', 'total_price']
    list_filter = ['start_date', 'bike__bike_model__brand']
    search_fields = ['client__name', 'bike__bike_model__model']

class BikeTypeAdmin(ImportExportModelAdmin):
    list_display = ['type', 'order']
    list_editable = ['order']

class RidePurposeAdmin(ImportExportModelAdmin):
    list_display = ['name']

class ProviderServiceInline(admin.TabularInline):
    model = ProviderService
    extra = 1

class BikeProviderAdmin(ImportExportModelAdmin):
    list_display = ['name', 'address', 'contact']
    inlines = [ProviderServiceInline]

class ProviderServiceAdmin(ImportExportModelAdmin):
    list_display = ['name', 'provider', 'availability', 'price']
    list_filter = ['availability', 'provider']

class PriceAdmin(ImportExportModelAdmin):
    resource_class = PriceResource
    list_display = ['bike', 'day1_price', 'week_price', 'month_price']
    list_filter = ['bike__bike_model__brand']
    search_fields = ['bike__bike_model__model']

admin.site.register(BikeModel, BikeModelAdmin)
admin.site.register(BikeBrand, BikeBrandAdmin)
admin.site.register(Client, ClientAdmin)
admin.site.register(BikeOrder, BikeOrderAdmin)
admin.site.register(BikeType, BikeTypeAdmin)
admin.site.register(RidePurpose, RidePurposeAdmin)
admin.site.register(BikeProvider, BikeProviderAdmin)
admin.site.register(ProviderService, ProviderServiceAdmin)
admin.site.register(Price, PriceAdmin)
