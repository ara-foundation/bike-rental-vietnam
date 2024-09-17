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
from .models import Bike, BikeBrand, BikeModel, BikeOrder, BikeType, RidePurpose
from .utils import get_total_bikes_for_brand


def bike_rental_view(request):
    context = {
        'brands': BikeBrand.objects.all(),
        'transmissions': Bike.objects.values_list('bike_model__transmission', flat=True).distinct(),
        'bike_types': BikeType.objects.all(),
        'ride_purposes': RidePurpose.objects.all(),
        'selected_brand': request.GET.get('brand', ''),
        'selected_transmission': request.GET.get('transmission', ''),
        'selected_bike_type': request.GET.get('bike_type', ''),
        'selected_ride_purpose': request.GET.get('ride_purpose', ''),
        'selected_gears': request.GET.get('gears', ''),
        'selected_fuel_system': request.GET.get('fuel_system', ''),
        'selected_displacement': request.GET.get('displacement', ''),
        'selected_clearance': request.GET.get('clearance', ''),
        'selected_weight': request.GET.get('weight', ''),
    }
    return render(request, 'bike_rental.html', context)

class BikeModelListView(ListView):
    model = BikeModel
    template_name = "bike_rental.html"  # Измените это
    context_object_name = "bike_rental"
    paginate_by = 9
    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            bikes_count=Count("bikes"),
            min_price=Min("bikes__price_per_day"),
            suppliers_count=Count("bikes__owner", distinct=True),
        )
        
        filters = {}
        selected_brands = self.request.GET.get('brand')
        if selected_brands:
            brand_ids = selected_brands.split(',')
            filters['brand_id__in'] = brand_ids  # Используем фильтрацию по множеству

        filters = {k: v for k, v in filters.items() if v is not None}

        if filters:
            queryset = queryset.filter(**filters)

        return queryset


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_fields = ['brand', 'transmission', 'gears', 'fuel_system', 'displacement', 'clearance', 'weight']

        for field in filter_fields:
            value = self.request.GET.get(field)
            if value and value != 'None':
                context[f'selected_{field}'] = value
            else:
                context[f'selected_{field}'] = None

        context["brands"] = BikeBrand.objects.filter().distinct()

        context["transmissions"] = (
            Bike.objects.filter(bike_model__isnull=False)
            .values_list("bike_model__transmission", flat=True)
            .distinct()
        )
        selected_brand_id = self.request.GET.get("brand")
        if selected_brand_id and selected_brand_id != 'None' and selected_brand_id != 'all':
            context["selected_brand"] = int(selected_brand_id)
            bike_brand_name = BikeBrand.objects.get(id=selected_brand_id).name
            context["selected_brand_name"] = bike_brand_name
            context["total_bikes_for_brand"] = get_total_bikes_for_brand(selected_brand_id)
        else:
            context["selected_brand"] = 'all'
            context["selected_brand_name"] = None
            context["total_bikes_for_brand"] = None

        context["bike_rental_count"] = self.get_queryset().count()

        gears = (
            BikeModel.objects.filter(transmission__in=["semi-auto", "manual"])
            .values_list("gears", flat=True)
            .distinct()
            .order_by("gears")
        )
        fuel_systems = (
            BikeModel.objects.values_list("fuel_system", flat=True)
            .distinct()
            .order_by("fuel_system")
        )
        displacements = (
            BikeModel.objects.values_list("displacement", flat=True)
            .distinct()
            .order_by("displacement")
        )
        clearance = (
            BikeModel.objects.values_list("clearance", flat=True)
            .distinct()
            .order_by("clearance")
        )
        weights = (
            BikeModel.objects.values_list("weight", flat=True)
            .distinct()
            .order_by("weight")
        )

        context["gears"] = gears
        context["fuel_systems"] = fuel_systems
        context["displacements"] = displacements
        context["clearance"] = clearance
        context["weights"] = weights

        context['selected_gears'] = self.request.GET.get('gears')
        context['selected_fuel_system'] = self.request.GET.get('fuel_system')
        context['selected_displacement'] = self.request.GET.get('displacement')
        context['selected_clearance'] = self.request.GET.get('clearance')
        context['selected_weight'] = self.request.GET.get('weight')
        context['selected_seat_height'] = self.request.GET.get('seat_height')
        context['selected_price_category'] = self.request.GET.get('price_category')

        applied_filters = {}

        search_query = self.request.GET.get('search', '')
        if search_query:
            applied_filters['search'] = search_query

        context['applied_filters'] = applied_filters
        
        context['bike_types'] = BikeType.objects.all().order_by('-id')
        context['ride_purposes'] = RidePurpose.objects.all()
        context['weight_categories'] = ['Light', 'Middle', 'Heavy']

        context["clearances"] = (
            BikeModel.objects.values_list("clearance", flat=True)
            .distinct()
            .order_by("clearance")
        )
        context['selected_clearance'] = self.request.GET.get('clearance')

        return add_design_settings(context)


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
        "name": f"Велотур {tour_id}",
        "description": f"Захватывающий велотур с красивыми видами и "
        f"интересными маршрутами. Тур номер {tour_id}.",
        "direction": random.choice([
            "Горы",
            "Побережье",
            "Город",
            "Сельская местность"
        ]),
        "duration": random.randint(1, 10),
        "date": (datetime.now() + timedelta(days=random.randint(1, 30))).strftime(
            "%Y-%m-%d"),
        "difficulty": random.choice(["Легкий", "Средний", "Сложный"]),
        "price": random.randint(50, 500),
        "themes": random.sample(
            ["Природа", "История", "Культура", "Приключения", "Гастрономия"],
            k=random.randint(1, 3)),
        "route": [f"Точка {i}" for i in range(1, random.randint(3, 8))],
        "included": ["Велосипед", "Шлем", "Питание", "Проживание", "Гид"],
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