from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django_filters.views import FilterView
from django.core.paginator import Paginator
from .models import BikeModel, Bike, Order
from .filters import BikeModelFilter
from django.urls import reverse
from .forms import ClientForm, OrderForm

class BikeModelListView(FilterView):
    model = BikeModel
    filterset_class = BikeModelFilter
    template_name = 'bikemodel_list.html'
    paginate_by = 10

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