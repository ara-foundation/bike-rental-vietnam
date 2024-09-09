from django.urls import path

from .views import (
    BikeModelListView,
    bike_offer,
    bike_order,
    bikemodel_detail,
    order_confirmation,
)

# from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    path("", BikeModelListView.as_view(), name="bikemodel_list"),
    path("bikemodels/", BikeModelListView.as_view(), name="bikemodel_list"),
    path("bikemodel/<int:id>/", bikemodel_detail, name="bikemodel_detail"),
    path("bike/<int:id>/", bike_offer, name="bike_offer"),
    path("bike/<int:id>/order/", bike_order, name="bike_order"),
    path(
        "order/<int:order_id>/confirmation/",
        order_confirmation,
        name="order_confirmation",
    ),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
