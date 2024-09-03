from django.urls import path
from .views import BikeModelListView, bikemodel_detail

urlpatterns = [
    path('bikemodels/', BikeModelListView.as_view(), name='bikemodel_list'),  # Использует BikeModelListView для списка моделей
    path('bikemodel/<int:id>/', bikemodel_detail, name='bikemodel_detail'),  # Для детального просмотра модели
]
