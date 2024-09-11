from django.contrib import admin

from tours.models import (
    AdditionalOption,
    CabinType,
    FreeOfChargeService,
    Lunch,
    Photo,
    Route,
    Ship,
    Tour,
    TourDate,
    TourOrder,
)


@admin.register(Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "start_date",
        "pick_up_time",
        "duration",
        "cost_per_person",
        "ship",
        "author",
    )
    list_editable = (
        "start_date",
        "pick_up_time",
        "duration",
        "cost_per_person",
        "ship",
    )
    search_fields = ("name",)
    filter_horizontal = (
        "tour_photo_gallery",
        "free_services",
        "additional_options",
        "lunch",
        "route",
    )
    exclude = ("author",)

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related("author", "ship", "start_date")
            .prefetch_related(
                "tour_photo_gallery",
                "lunch",
                "route",
                "free_services",
                "additional_options",
            )
        )

        # To cache the group check to avoid repeated queries
        is_tour_provider = request.user.groups.filter(name="Tour Provider").exists()

        if is_tour_provider:
            return qs.filter(author=request.user)
        if request.user.is_superuser:
            return qs
        return qs.none()

    def has_change_permission(self, request, obj=None):
        # Allow tour providers to edit only their own tours
        if (
            obj is not None
            and request.user.groups.filter(name="Tour Provider").exists()
        ):
            return obj.author == request.user
        return super().has_change_permission(request, obj)

    def has_view_permission(self, request, obj=None):
        # Allow tour providers to view only their own tours
        if (
            obj is not None
            and request.user.groups.filter(name="Tour Provider").exists()
        ):
            return obj.author == request.user
        return super().has_view_permission(request, obj)

    def has_add_permission(self, request):
        # Allow tour providers to add tours
        if request.user.groups.filter(name="Tour Provider").exists():
            return True
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Tour providers should not have permission to delete tours
        if request.user.groups.filter(name="Tour Provider").exists():
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change or obj.author is None:
            # Automatically set the author to the
            # logged-in user if this is a new object or if author is not set
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(TourOrder)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "tour",
        "date",
        "email_of_initiator",
        "phone_number",
        "messenger",
        "author",
    )
    search_fields = ("email_of_initiator", "phone_number", "messenger")
    exclude = ("author",)

    def get_queryset(self, request):
        # Get the base queryset
        qs = super().get_queryset(request)

        # Check if the user is part of the "Tour Provider" group
        if request.user.groups.filter(name="Tour Provider").exists():
            # Filter orders to show only those related to tours the provider has created
            return qs.filter(tour__author=request.user)

        # Check if the user is part of the "Client Group" group
        if request.user.groups.filter(name="Client Group").exists():
            # Filter orders to show only those created by
            # the client (based on the author field)
            return qs.filter(author=request.user)

        # For superusers, return all orders
        if request.user.is_superuser:
            return qs

        # In all other cases (if a user is not in any group), return an empty queryset
        return qs.none()

    def save_model(self, request, obj, form, change):
        if not change or obj.author is None:
            # Automatically set the author to the
            # logged-in user if this is a new object or if author is not set
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ("description",)


@admin.register(TourDate)
class TourDateAdmin(admin.ModelAdmin):
    list_display = ("date",)


@admin.register(FreeOfChargeService)
class FreeOfChargeServiceAdmin(admin.ModelAdmin):
    list_display = (
        "service_name",
        "service_description",
    )


@admin.register(AdditionalOption)
class AdditionalOptionAdmin(admin.ModelAdmin):
    list_display = ("option_name", "option_description")


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
