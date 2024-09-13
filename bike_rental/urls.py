from django.urls import path
from .views import BikeModelListView, bike_rental_offers, bike_order, bike_offer, order_confirmation, bike_tours, car_tours, boat_tours, bike_tour_order,bike_tour

urlpatterns = [
    # Существующие маршруты
    path('', BikeModelListView.as_view(), name='bike_rental'),  # Обновите name, если необходимо
    path('bike_rental/', BikeModelListView.as_view(), name='bike_rental'),
    path('bike_rental_offers/<str:brand>/<int:id>/', bike_rental_offers, name='bike_rental_offers'),
    path('bike/<int:id>/', bike_offer, name='bike_offer'),
    path('bike/<int:id>/order/', bike_order, name='bike_order'),
    path('order/<int:order_id>/confirmation/', order_confirmation, name='order_confirmation'),
    path('bike-tours/', bike_tours, name='bike_tours'),
    path('car-tours/', car_tours, name='car_tours'),
    path('boats-tours/', boat_tours, name='boat_tours'),
    path('bike-tour-order/<int:tour_id>/', bike_tour_order, name='bike_tour_order'),
    path('bike-tour/<int:tour_id>/', bike_tour, name='bike_tour'),
]
# from django.conf import settings
# from django.conf.urls.static import static
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
