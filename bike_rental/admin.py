from django.contrib import admin
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from .models import Bike, BikeBrand, BikeModel, BikeOrder, Client, BikeType, RidePurpose, BikeProvider, ProviderService, Price, Promouter, Season
from .resources import BikeModelResource, BikeResource, PriceResource, PromouterResource, BikeOrderResource, SeasonResource
# import datetime
@admin.register(BikeBrand)
class BikeBrandAdmin(ImportExportModelAdmin):
    list_display = ["name", "logo_preview"]
    readonly_fields = ["logo_preview"]

    def logo_preview(self, obj):
        if obj.logo:
            return mark_safe(f'<img src="{obj.logo.url}" width="100" height="100" />')
        return "No logo"

    logo_preview.short_description = "Logo preview"
    
@admin.register(BikeModel)
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
    list_display = ["bike_model", "amount", "get_price", "availability", "get_bike_provider"] 
    list_filter = ["availability", "bike_model__brand", "bike_provider"]
    search_fields = ["bike_model__brand__name", "bike_model__model", "bike_provider__name"]
    readonly_fields = ["photo_preview"]
    inlines = [PriceInline]

    def get_price(self, obj):
        #today = datetime.date.today()
        today = timezone.now().date()
        season = Season.objects.filter(
            start_date__lte=today,
            close_date__gte=today,
            bike_provider=obj.bike_provider
        ).first()
        
        if season:
            price = Price.objects.filter(
                bike=obj,
                season=season,
                duration=1  # Предполагаем, что хотим показать цену за 1 день
            ).first()
            
            if price:
                return f"{price.cost} ({season.name})"
        
        return "N/A"
    get_price.short_description = "Price (1 day)"  # Исправлена опечатка
    # get_price.short_descriptipriceon = "Price (1 day)"

    def get_bike_provider(self, obj):
        return obj.bike_provider.name
    get_bike_provider.short_description = "Bike Provider"

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)

        # Check if the user is part of the "Bike Provider" group
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
    
@admin.register(Client)
class ClientAdmin(ImportExportModelAdmin):
    list_display = ['name', 'contact']
    search_fields = ['name', 'contact']

@admin.register(BikeOrder)
class BikeOrderAdmin(ImportExportModelAdmin):
    resource_class = BikeOrderResource
    list_display = ['id', 'get_bike_brand', 'get_bike_model', 'start_date', 'duration', 'amount_bikes', 'total_price', 'get_client_name', 'get_client_contact']
    list_filter = ['start_date', 'bike__bike_model__brand', 'bike__bike_model']
    search_fields = ['bike__bike_model__brand__name', 'bike__bike_model__model', 'client__name', 'client__contact']

    def get_bike_brand(self, obj):
        return obj.bike.bike_model.brand.name
    get_bike_brand.short_description = 'Bike Brand'

    def get_bike_model(self, obj):
        return obj.bike.bike_model.model
    get_bike_model.short_description = 'Bike Model'

    def get_client_name(self, obj):
        return obj.client.name
    get_client_name.short_description = 'Client Name'

    def get_client_contact(self, obj):
        return obj.client.contact
    get_client_contact.short_description = 'Client Contact'
    
@admin.register(BikeType)
class BikeTypeAdmin(ImportExportModelAdmin):
    list_display = ['type', 'order']
    list_editable = ['order']

@admin.register(RidePurpose)
class RidePurposeAdmin(ImportExportModelAdmin):
    list_display = ['name']

class ProviderServiceInline(admin.TabularInline):
    model = ProviderService
    extra = 1
    
@admin.register(BikeProvider)
class BikeProviderAdmin(ImportExportModelAdmin):
    list_display = ['name', 'address', 'contact']
    inlines = [ProviderServiceInline]

class ProviderServiceAdmin(ImportExportModelAdmin):
    list_display = ['name', 'provider', 'availability', 'price']
    list_filter = ['availability', 'provider']

@admin.register(Price)
class PriceAdmin(ImportExportModelAdmin):
    resource_class = PriceResource
    list_display = ['bike', 'season', 'duration', 'cost']
    list_filter = ['bike__bike_model__brand', 'season', 'duration', 'cost']
    search_fields = ['bike__bike_model__model', 'season__name']

@admin.register(Promouter)
class PromouterAdmin(ImportExportModelAdmin):
    resource_class = PromouterResource
    list_display = ['user', 'promo_pyte', 'id', 'comition_percent']
    search_fields = ['user__username', 'id']

class SeasonInline(admin.TabularInline):
    model = Season
    extra = 1

@admin.register(Season)
class SeasonAdmin(ImportExportModelAdmin):
    resource_class = SeasonResource
    list_display = ['name', 'start_date', 'close_date', 'bike_provider']
    list_filter = ['bike_provider']    

# Повторная регистрация с новыми настройками
# @admin.register(BikeProvider)
# class BikeProviderAdmin(admin.ModelAdmin):
#     # Ваши новые настройки здесь
#     pass
