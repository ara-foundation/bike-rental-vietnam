from django.urls import path
from .views import BikeModelListView, bikemodel_detail, bike_offer, bike_order, order_confirmation, get_models, get_transmissions
from django.conf import settings
# from django.conf.urls.static import static

urlpatterns = [
    path('', BikeModelListView.as_view(), name='bikemodel_list'),
    path('get_models/', get_models, name='get_models'),
    path('get_transmissions/', get_transmissions, name='get_transmissions'),
    path('bikemodels/', BikeModelListView.as_view(), name='bikemodel_list'),
    path('bikemodel/<int:id>/', bikemodel_detail, name='bikemodel_detail'),
    path('bike/<int:id>/', bike_offer, name='bike_offer'),
    path('bike/<int:id>/order/', bike_order, name='bike_order'),
    path('order/<int:order_id>/confirmation/', order_confirmation, name='order_confirmation'),
    # path('get_models_and_transmissions/', get_models_and_transmissions, name='get_models_and_transmissions'),
    # path('get_brand_and_transmission/', get_brand_and_transmission, name='get_brand_and_transmission'),
]
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

