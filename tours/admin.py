from django.contrib import admin

from tours.models import Tour, Photo, TourDate, FreeOfChargeService, AdditionalOption, \
    Route, Ship, CabinType, Lunch


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'pick_up_time', 'duration', 'cost')
    search_fields = ('name',)
    filter_horizontal = (
    'tour_photo_gallery', 'free_services', 'additional_options')

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('description',)

@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ('date',)

@admin.register(FreeOfChargeService)
class FreeOfChargeServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'service_description',)

@admin.register(AdditionalOption)
class AdditionalOptionAdmin(admin.ModelAdmin):
    list_display = ('option_name', 'option_description')

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "description")

@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ("name", "type")

@admin.register(CabinType)
class CabinTypeAdmin(admin.ModelAdmin):
    list_display = ("type", "description")

@admin.register(Lunch)
class LunchAdmin(admin.ModelAdmin):
    list_display = ("name", "ingredients")