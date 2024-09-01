from rest_framework import viewsets
from tours.models import Tour

from api.serializers import TourSerializer


# Create your views here.
class TourViewSet(viewsets.ModelViewSet):
    queryset = Tour.objects.all().select_related("author")
    serializer_class = TourSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
