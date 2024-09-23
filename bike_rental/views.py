import random
from datetime import datetime, timedelta

from django.conf import settings

from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.db.models import Count, Min, Q, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.http import JsonResponse
from .forms import ClientForm, OrderForm
from .models import Bike, BikeBrand, BikeModel, BikeOrder, BikeType, RidePurpose, BikeProvider, ProviderService
from .utils import get_total_bikes_for_brand
from django.utils.http import urlencode



class BikeModelListView(ListView):
    model = BikeModel
    template_name = "bike_rental.html"
    context_object_name = "bike_rental"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = {}

        # Обработка фильтров по типу велосипеда
        bike_types = self.request.GET.get('bike_type', '').split(',')
        bike_types = [bt for bt in bike_types if bt.strip().isdigit()]
        if bike_types:
            filters['bike_type__id__in'] = bike_types

        # Обработка фильтров по цели поездки
        ride_purposes = [rp for rp in self.request.GET.getlist('ride_purpose') if rp.isdigit()]
        if ride_purposes:
            filters['ride_purposes__id__in'] = ride_purposes

        # Обработка фильтров по бренду
        brands = self.request.GET.get('brand', '').split(',')
        brands = list(set([b.strip() for b in brands if b.strip().isdigit()]))
        if brands:
            filters['brand__id__in'] = brands

        
        # Фильтр поиска

        search_query = self.request.GET.get('search')

        if search_query:
            filters['Q'] = Q(brand__name__icontains=search_query) | Q(model__icontains=search_query)

        # Обработка фильтров по цене
        price_categories = self.request.GET.getlist('price_category')
        if price_categories:
            price_filters = Q()
            for category in price_categories:
                if category == 'Budget':
                    price_filters |= Q(bike__price_per_day__lte=50)
                elif category == 'Standard':
                    price_filters |= Q(bike__price_per_day__gt=50, bike__price_per_day__lte=100)
                elif category == 'Premium':
                    price_filters |= Q(bike__price_per_day__gt=100)
            filters['Q'] = filters.get('Q', Q()) & price_filters

        # Обработка фильтров по высоте сиденья
        seat_heights = self.request.GET.getlist('seat_height')
        if seat_heights:
            height_filters = Q()
            for height in seat_heights:
                if height == 'Low':
                    height_filters |= Q(seat_height__lt=170)
                elif height == 'Middle':
                    height_filters |= Q(seat_height__gte=170, seat_height__lte=180)
                elif height == 'High':
                    height_filters |= Q(seat_height__gt=180)
            filters['Q'] = filters.get('Q', Q()) & height_filters

        # Обработка фильтров по весу
        weights = self.request.GET.getlist('weight')
        if weights:
            weight_filters = Q()
            for weight in weights:
                if weight == 'Light':
                    weight_filters |= Q(weight__lte=120)
                elif weight == 'Middle':
                    weight_filters |= Q(weight__gt=120, weight__lte=180)
                elif weight == 'Heavy':
                    weight_filters |= Q(weight__gt=180)
            filters['Q'] = filters.get('Q', Q()) & weight_filters

        # Expert Filters
        expert_filters = ['transmission', 'gears', 'fuel_system', 'displacement', 'clearance']
        for filter_name in expert_filters:
            value = self.request.GET.get(filter_name)
            if value and value != 'None':
                filters[f'{filter_name}__iexact'] = value

        print("Filters being applied:", filters)

        if 'Q' in filters:
            queryset = queryset.filter(filters.pop('Q'))
        return queryset.filter(**filters).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['bike_types'] = BikeType.objects.all().order_by('-id')
        context['ride_purposes'] = RidePurpose.objects.all()
        context['brands'] = BikeBrand.objects.all()
        context['transmissions'] = BikeModel.objects.values_list('transmission', flat=True).distinct().order_by('transmission')
        context['gears'] = BikeModel.objects.values_list('gears', flat=True).distinct().order_by('gears')
        context['fuel_systems'] = BikeModel.objects.values_list('fuel_system', flat=True).distinct().order_by('fuel_system')
        context['displacements'] = BikeModel.objects.values_list('displacement', flat=True).distinct().order_by('displacement')
        context['clearances'] = BikeModel.objects.values_list('clearance', flat=True).distinct().order_by('clearance')
        context['theme_color'] = settings.THEME_COLOR

        # Applied filters
        applied_filters = {}
        for key, values in self.request.GET.lists():
            if values and key not in ['page', 'csrfmiddlewaretoken']:
                # Удаляем пустые значения
                filtered_values = list(filter(None, values))
                if filtered_values:
                    applied_filters[key] = list(dict.fromkeys(filtered_values))
        
        # Логируем очищенные фильтры
        print("Applied Filters:", applied_filters)

        # Очистка старых фильтров перед сохранением
        self.request.session['applied_filters'] = {}

        # Сохранение новых фильтров в сессии
        self.request.session['applied_filters'] = applied_filters

        context['applied_filters'] = applied_filters

        # Selected filters
        for filter_name in ['bike_type', 'ride_purpose', 'brand', 'price_category', 'seat_height', 'weight']:
            context[f'selected_{filter_name}s'] = self.request.GET.getlist(filter_name)

        for filter_name in ['transmission', 'gears', 'fuel_system', 'displacement', 'clearance']:
            context[f'selected_{filter_name}'] = self.request.GET.get(filter_name)

        context['bike_rental_count'] = self.get_queryset().count()

        return context

    def get(self, request, *args, **kwargs):
        # Восстановление фильтров из сессии, если GET-параметры пусты
        if not request.GET:
            saved_filters = request.session.get('applied_filters', {})
            if saved_filters:
                return redirect(f"{request.path}?{urlencode(saved_filters, doseq=True)}")
        return super().get(request, *args, **kwargs)


def bike_rental_offers(request, brand, id):
    bikemodel = get_object_or_404(BikeModel, brand__name=brand, id=id)
    bikes = Bike.objects.filter(bike_model=bikemodel)
    context = {"bikemodel": bikemodel, "bikes": bikes}
    context = add_design_settings(context)
    return render(request, "bike_rental_offers.html", context)


def bike_offer(request, id):
    bike = get_object_or_404(Bike, id=id)
    context = {"bike": bike}
    context = add_design_settings(context)
    return render(request, "bike_offer.html", context)


def bike_order(request, id):
    bike = get_object_or_404(Bike, id=id)
    if request.method == "POST":
        client_form = ClientForm(request.POST)
        order_form = OrderForm(request.POST, bike=bike)
        if client_form.is_valid() and order_form.is_valid():
            client = client_form.save()
            order = order_form.save(commit=False)

            start_date = order_form.cleaned_data["start_date"]
            current_year = datetime.now().year
            order.start_date = start_date.replace(year=current_year)

            order.client = client
            order.bike = bike
            order.total_price = calculate_total_price(
                bike, order.duration, order.amount_bikes
            )
            order.save()
            return redirect(
                reverse("order_confirmation", kwargs={"order_id": order.id})
            )
    else:
        client_form = ClientForm()
        order_form = OrderForm()

    context = {"bike": bike, "client_form": client_form, "order_form": order_form}
    context = add_design_settings(context)
    return render(request, "bike_order.html", context)


def calculate_total_price(bike, duration, amount_bikes):
    return bike.price_per_day * duration * amount_bikes


def order_confirmation(request, order_id):
    order = get_object_or_404(BikeOrder, id=order_id)
    context = {"order": order}
    context = add_design_settings(context)
    return render(request, "order_confirmation.html", context)


def add_design_settings(context):
    context["theme_color"] = settings.THEME_COLOR
    context["custom_css"] = settings.CUSTOM_CSS
    return context


def bike_tours(request):
    tours = range(1, 16)
    paginator = Paginator(tours, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "paginate_by": 10,
    }
    context = add_design_settings(context)
    return render(request, "bike_tours.html", context)


def car_tours(request):
    tours = range(1, 16)
    paginator = Paginator(tours, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "paginate_by": 5,
    }
    context = add_design_settings(context)
    return render(request, "car_tours.html", context)


def boat_tours(request):
    tours = range(1, 16)
    paginator = Paginator(tours, 8)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "paginate_by": 8,
    }
    context = add_design_settings(context)
    return render(request, "boat_tours.html", context)


def bike_tour_order(request, tour_id):
    difficulty_levels = ["Easy", "Intermediate", "Hard"]
    themes = ["Mountain", "City", "Countryside", "Coastal"]

    context = {
        "tour_id": tour_id,
        "difficulty": random.choice(difficulty_levels),
        "themes": random.sample(themes, k=random.randint(1, 3)),
    }

    if request.method == "POST":
        context.update({
            "booking_date": request.POST.get("date"),
            "participants": request.POST.get("participants"),
        })
        return render(request, "bike_tour_order_confirmation.html", context)

    return render(request, "bike_tour_order.html", context)


def bike_tour(request, tour_id):
    tour = {
        "id": tour_id,
        "name": f"Bike Tour {tour_id}",
        "description": f"An exciting bike tour with beautiful views and "
        f"interesting routes. Tour number {tour_id}.",
        "direction": random.choice([
            "Mountains",
            "Coast",
            "City",
            "Countryside"
        ]),
        "duration": random.randint(1, 10),
        "date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime(
            "%Y-%m-%d"),
        "difficulty": random.choice(["Easy", "Intermediate", "Hard"]),
        "price": random.randint(50, 500),
        "themes": random.sample(
            ["Nature", "History", "Culture", "Adventure", "Gastronomy"],
            k=random.randint(1, 3)),
        "route": [f"Point {i}" for i in range(1, random.randint(3, 8))],
        "included": ["Bike", "Helmet", "Food", "Accommodation", "Guide"],
    }

    return render(request, "bike_tour.html", {"tour": tour})


def autocomplete(request):
    query = request.GET.get('term', '')
    brands = BikeBrand.objects.filter(name__icontains=query).values_list('name', flat=True)
    models = BikeModel.objects.filter(model__icontains=query).values_list('model', flat=True)
    brand_models = BikeModel.objects.filter(
        Q(brand__name__icontains=query) | Q(model__icontains=query)
    ).annotate(
        full_name=Concat('brand__name', Value(' '), 'model')
    ).values_list('full_name', flat=True)
    
    results = list(brands) + list(models) + list(brand_models)
    return JsonResponse(results, safe=False)


def remove_filter(request):
    print("Current GET parameters:", request.GET)  # Отладка
    current_filters = request.GET.copy()
    filter_to_remove = request.GET.get('filter_to_remove')
    value_to_remove = request.GET.get('value_to_remove')

    print(f"Removing filter: {filter_to_remove}, value: {value_to_remove}")  # Отладка

    if filter_to_remove and value_to_remove:
        values = current_filters.getlist(filter_to_remove)
        print(f"Current values for {filter_to_remove}: {values}")  # Отладка
        if value_to_remove in values:
            values.remove(value_to_remove)
            if values:
                current_filters.setlist(filter_to_remove, values)
            else:
                del current_filters[filter_to_remove]

    current_filters.pop('page', None)  # Удаляем параметр страницы, если он есть
    return redirect(f"{request.path}?{current_filters.urlencode()}")
