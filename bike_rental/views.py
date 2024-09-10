from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
# from django_filters.views import FilterView
from django.core.paginator import Paginator
from .models import BikeModel, Bike, Order, BikeBrand
from django.urls import reverse
from .forms import ClientForm, OrderForm
from django.views.generic import ListView
from datetime import datetime
from django.conf import settings
import random

class BikeModelListView(ListView):
    model = BikeModel
    template_name = 'bikemodel_list.html'
    context_object_name = 'bikemodels'
    paginate_by = 9

    def get_queryset(self):
        queryset = BikeModel.objects.all()
        brand = self.request.GET.get('brand')
        transmission = self.request.GET.get('transmission')

        if brand:
            queryset = queryset.filter(brand_id=brand)
        if transmission:
            queryset = queryset.filter(transmission=transmission)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['brands'] = BikeBrand.objects.all()
        
        transmissions = set(BikeModel.objects.values_list('transmission', flat=True))
        transmission_order = ['auto', 'semi-auto', 'manual']
        sorted_transmissions = [t for t in transmission_order if t in transmissions] + sorted(transmissions - set(transmission_order))
        context['transmissions'] = sorted_transmissions
        
        selected_brand_id = self.request.GET.get('brand')
        if selected_brand_id:
            context['selected_brand'] = int(selected_brand_id)
            context['selected_brand_name'] = BikeBrand.objects.get(id=selected_brand_id).name
        else:
            context['selected_brand'] = None
        
        context['selected_transmission'] = self.request.GET.get('transmission')
        if context['selected_brand']:
            context['selected_brand_name'] = BikeBrand.objects.get(id=context['selected_brand']).name
        context['bikemodels_count'] = self.get_queryset().count()
        return add_design_settings(context)

def bikemodel_detail(request, id):
    bikemodel = get_object_or_404(BikeModel, id=id)
    bikes = Bike.objects.filter(bike_model=bikemodel)
    context = {'bikemodel': bikemodel, 'bikes': bikes}
    context = add_design_settings(context)
    return render(request, 'bikemodel_detail.html', context)

def bike_offer(request, id):
    bike = get_object_or_404(Bike, id=id)
    context = {'bike': bike}
    context = add_design_settings(context)
    return render(request, 'bike_offer.html', context)

def bike_order(request, id):
    bike = get_object_or_404(Bike, id=id)
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        order_form = OrderForm(request.POST, bike=bike)
        if client_form.is_valid() and order_form.is_valid():
            client = client_form.save()
            order = order_form.save(commit=False)
            
            # Добавляем текущий год к дате
            start_date = order_form.cleaned_data['start_date']
            current_year = datetime.now().year
            order.start_date = start_date.replace(year=current_year)
            
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
    context = add_design_settings(context)
    return render(request, 'bike_order.html', context)

def calculate_total_price(bike, duration, amount_bikes):
    # Implement your pricing logic here
    return bike.price_per_day * duration * amount_bikes

def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    context = add_design_settings(context)
    return render(request, 'order_confirmation.html', context)

def add_design_settings(context):
    context['theme_color'] = settings.THEME_COLOR
    context['custom_css'] = settings.CUSTOM_CSS
    return context

def bike_tours(request):
    tours = range(1, 16)  # 15 тестовых туров
    paginator = Paginator(tours, 10)  # 10 туров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginate_by': 10,
    }
    context = add_design_settings(context)
    return render(request, 'bike_tours.html', context)

def car_tours(request):
    tours = range(1, 16)  # 15 тестовых туров
    paginator = Paginator(tours, 5)  # 5 туров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginate_by': 5,
    }
    context = add_design_settings(context)
    return render(request, 'car_tours.html', context)

def boat_tours(request):
    tours = range(1, 16)  # 15 тестовых туров
    paginator = Paginator(tours, 8)  # 8 туров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'paginate_by': 8,
    }
    context = add_design_settings(context)
    return render(request, 'boat_tours.html', context)

def bike_tour_order(request, tour_id):
    # Генерируем случайные данные для тура
    difficulty_levels = ['Easy', 'Intermediate', 'Hard']
    themes = ['Mountain', 'City', 'Countryside', 'Coastal']
    
    context = {
        'tour_id': tour_id,
        'difficulty': random.choice(difficulty_levels),
        'themes': random.sample(themes, k=random.randint(1, 3))
    }
    
    if request.method == 'POST':
        # Обработка отправленной формы
        context.update({
            'booking_date': request.POST.get('date'),
            'participants': request.POST.get('participants')
        })
        return render(request, 'bike_tour_order_confirmation.html', context)
    
    return render(request, 'bike_tour_order.html', context)

def bike_tour(request, tour_id):
    # Генерируем случайные данные для тура
    tour = {
        'id': tour_id,
        'name': f'Велотур {tour_id}',
        'description': f'Захватывающий велотур с красивыми видами и интересными маршрутами. Тур номер {tour_id}.',
        'direction': random.choice(['Горы', 'Побережье', 'Город', 'Сельская местность']),
        'duration': random.randint(1, 10),
        'date': (datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
        'difficulty': random.choice(['Легкий', 'Средний', 'Сложный']),
        'price': random.randint(50, 500),
        'themes': random.sample(['Природа', 'История', 'Культура', 'Приключения', 'Гастрономия'], k=random.randint(1, 3)),
        'route': [f'Точка {i}' for i in range(1, random.randint(3, 8))],
        'included': ['Велосипед', 'Шлем', 'Питание', 'Проживание', 'Гид'],
    }
    
    return render(request, 'bike_tour.html', {'tour': tour})
