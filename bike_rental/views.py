from django.shortcuts import render
from django.http import HttpResponse
from django_filters.views import FilterView
from django.core.paginator import Paginator
from .models import BikeModel
from .filters import BikeModelFilter

class BikeModelListView(FilterView):
    model = BikeModel
    filterset_class = BikeModelFilter
    template_name = 'bikemodel_list.html'  # Убедитесь, что этот шаблон существует
    paginate_by = 10  # Добавляем пагинацию

def bikemodel_detail(request, id):
    try:
        bikemodel = BikeModel.objects.get(id=id)
    except BikeModel.DoesNotExist:
        return HttpResponse("Model not found", status=404)

    context = {'bikemodel': bikemodel}
    return render(request, 'bikemodel_detail.html', context)  # Убедитесь, что этот шаблон существует