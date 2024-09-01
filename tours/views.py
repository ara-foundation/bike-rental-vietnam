from django.views.generic import ListView

from tours.models import Tour


class TourListView(ListView):
    model = Tour
    template_name = "tour/index.html"
