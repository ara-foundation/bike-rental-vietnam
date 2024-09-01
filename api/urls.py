from django.urls import include, path
from rest_framework import routers

from api.views import TourViewSet

app_name = "api"
router = routers.DefaultRouter()

router.register(r"tours", TourViewSet, basename="tours")

urlpatterns = [
    path("", include(router.urls)),
]
