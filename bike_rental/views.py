from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django_filters.views import FilterView
from django.core.paginator import Paginator
from .models import BikeModel, Bike, Order
from .filters import BikeModelFilter
from django.urls import reverse
from .forms import ClientForm, OrderForm
from django.views.generic import ListView

class BikeModelListView(ListView):
    model = BikeModel
    template_name = 'bikemodel_list.html'
    context_object_name = 'bikemodels'
    paginate_by = 9  # Установите количество объектов на страницу

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = BikeModelFilter(self.request.GET, queryset=queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = self.filterset
        return context

def bikemodel_detail(request, id):
    bikemodel = get_object_or_404(BikeModel, id=id)
    bikes = Bike.objects.filter(bike_model=bikemodel)
    context = {'bikemodel': bikemodel, 'bikes': bikes}
    return render(request, 'bikemodel_detail.html', context)

def bike_offer(request, id):
    bike = get_object_or_404(Bike, id=id)
    context = {'bike': bike}
    return render(request, 'bike_offer.html', context)

def bike_order(request, id):
    bike = get_object_or_404(Bike, id=id)
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        order_form = OrderForm(request.POST, bike=bike)
        if client_form.is_valid() and order_form.is_valid():
            client = client_form.save()
            order = order_form.save(commit=False)
            order.client = client
            order.bike = bike
            order.total_price = calculate_total_price(bike, order.duration, order.amount_bikes)
            order.save()
            return redirect(reverse('order_confirmation', kwargs={'order_id': order.id}))
    else:
        client_form = ClientForm()
        order_form = OrderForm()
    
    context = {
        'bike': bike,
        'client_form': client_form,
        'order_form': order_form
    }
    return render(request, 'bike_order.html', context)

def calculate_total_price(bike, duration, amount_bikes):
    # Implement your pricing logic here
    return bike.price_per_day * duration * amount_bikes

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'order_confirmation.html', context)

def get_models(request):
    brand_id = request.GET.get('brand')
    models = BikeModel.objects.filter(brand_id=brand_id).values('id', 'model')
    return JsonResponse(list(models), safe=False)

def get_transmissions(request):
    model_id = request.GET.get('model')
    transmissions = BikeModel.objects.filter(id=model_id).values_list('transmission', flat=True).distinct()
    return JsonResponse(list(transmissions), safe=False)

def get_models_and_transmissions(request):
    brand_id = request.GET.get('brand_id')
    models_and_transmissions = BikeModel.objects.filter(brand_id=brand_id).values('id', 'model', 'transmission').distinct()
    return JsonResponse(list(models_and_transmissions), safe=False)

def get_brand_and_transmission(request):
    model_id = request.GET.get('model_id')
    bike_model = BikeModel.objects.get(id=model_id)
    data = {
        'brand_id': bike_model.brand_id,
        'transmission': bike_model.transmission
    }
    return JsonResponse(data)
