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
        filters = Q()  # Инициализируем пустой Q объект для фильтров

        # Получаем фильтры из сессии
        applied_filters = self.request.session.get('applied_filters', {}) or {}
        print("Применяемые фильтры:", applied_filters)  # Отладка

        # Обработка фильтров по типу велосипеда
        bike_types = applied_filters.get('bike_type', [])
        if bike_types:
            filters &= Q(bike_type__id__in=bike_types)
            print(f"Фильтры по типу велосипеда: {bike_types}")  # Отладка

        # Обработка фильтров по цели поездки
        ride_purposes = applied_filters.get('ride_purpose', [])
        if ride_purposes:
            filters &= Q(ride_purposes__id__in=ride_purposes)
            print(f"Фильтры по цели поездки: {ride_purposes}")  # Отладка

        # Обработка фильтров по бренду
        brands = applied_filters.get('brand', [])
        if brands:
            filters &= Q(brand__id__in=brands)
            print(f"Фильтры по бренду: {brands}")  # Отладка

        # Фильтр поиска
        search_query = applied_filters.get('search', '').strip()
        if search_query:
            filters &= (Q(brand__name__icontains=search_query) | Q(model__icontains=search_query))
            print(f"Фильтр поиска: {search_query}")  # Отладка

        # Обработка фильтров по цене
        price_categories = applied_filters.get('price_category', [])
        price_filters = Q()
        for category in price_categories:
            if category == 'Budget':
                price_filters |= Q(bike__price_per_day__lte=50)
            elif category == 'Standard':
                price_filters |= Q(bike__price_per_day__gt=50, bike__price_per_day__lte=100)
            elif category == 'Premium':
                price_filters |= Q(bike__price_per_day__gt=100)
        if price_filters:
            filters &= price_filters
            print(f"Фильтры по цене: {price_categories}")  # Отладка

        # Обработка фильтров по высоте сиденья
        seat_heights = applied_filters.get('seat_height', [])
        height_filters = Q()
        for height in seat_heights:
            if height == 'Low':
                height_filters |= Q(seat_height__lt=170)
            elif height == 'Middle':
                height_filters |= Q(seat_height__gte=170, seat_height__lte=180)
            elif height == 'High':
                height_filters |= Q(seat_height__gt=180)
        if height_filters:
            filters &= height_filters
            print(f"Фильтры по высоте сиденья: {seat_heights}")  # Отладка

        # Обработка фильтров по весу
        weights = applied_filters.get('weight', [])
        weight_filters = Q()
        for weight in weights:
            if weight == 'Light':
                weight_filters |= Q(weight__lte=120)
            elif weight == 'Middle':
                weight_filters |= Q(weight__gt=120, weight__lte=180)
            elif weight == 'Heavy':
                weight_filters |= Q(weight__gt=180)
        if weight_filters:
            filters &= weight_filters
            print(f"Фильтры по весу: {weights}")  # Отладка

        # Expert Filters
        expert_filters = ['transmission', 'gears', 'fuel_system', 'displacement', 'clearance']
        for filter_name in expert_filters:
            value = self.request.GET.get(filter_name)
            print(f"{filter_name} from request:", value)  # Отладка
            if value and value != 'None':
                filters &= Q(**{f'{filter_name}__iexact': value})
                print(f"Фильтр {filter_name}: {value}")  # Отладка

        # Применяем фильтры к queryset
        print("Финальный фильтр:", filters)  # Отладка
        return queryset.filter(filters).distinct()

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

        # Подсчет доступных моделей
        context['bike_rental_count'] = self.get_queryset().count()

        # Получаем актуальные фильтры из сессии
        context['applied_filters'] = self.applied_filters
        print("Applied filters in context:", context['applied_filters'])  # Отладка

        return context

    def get(self, request, *args, **kwargs):
        # Получаем актуальные фильтры из сессии
        self.applied_filters = request.session.get('applied_filters', {})
        print("Applied filters from session:", self.applied_filters)  # Отладка
        
        if 'filter_to_remove' in request.GET:
            remove_filter(request)
            # После удаления фильтра обновляем applied_filters
            self.applied_filters = request.session.get('applied_filters', {})
        
        return super().get(request, *args, **kwargs)

def remove_filter(request):
    current_filters = request.session.get('applied_filters', {})
    filter_to_remove = request.GET.get('filter_to_remove')
    value_to_remove = request.GET.get('value_to_remove')
    print(f"Удаляем фильтр: {filter_to_remove}, значение: {value_to_remove}")  # Отладка

    # if filter_to_remove and value_to_remove:
    #     if filter_to_remove in current_filters:
    #         values = current_filters[filter_to_remove]
    #         print(f"Текущие значения для {filter_to_remove}: {values}")  # Отладка
    #         # Удаляем значение, если оно есть в списке
    #         if value_to_remove in values:
    #             values.remove(value_to_remove)
    #             print(f"Значение {value_to_remove} удалено из {filter_to_remove}.")  # Отладка
    #             # Если список пустой, удаляем ключ
    #             if not values:
    #                 del current_filters[filter_to_remove]
    #                 print(f"Фильтр {filter_to_remove} удален, так как больше нет значений.")  # Отладка
    #         # Обновляем список, удаляя пустые строки
    #         current_filters[filter_to_remove] = [v for v in values if v]
    if filter_to_remove in current_filters:
        current_filters[filter_to_remove] = [v for v in current_filters[filter_to_remove] if v != value_to_remove]
        if not current_filters[filter_to_remove]:
            del current_filters[filter_to_remove]

    print("Обновленные фильтры:", current_filters)  # Отладка
    request.session['applied_filters'] = current_filters
    return redirect('bike_rental')

    
def filter_view(request):
    if request.method == 'GET':
        print("Данные GET-запроса:", request.GET)  # Отладка: вывод данных GET-запроса
        filter_data = {}
        for key, value in request.GET.items():
            if value:  # Проверяем, что значение не пустое
                filter_data[key] = value.split(',')  # Предполагаем, что параметры могут быть списками

        print("Данные для сохранения в сессию:", filter_data)  # Отладка: что сохраняем в сессию
        request.session['applied_filters'] = filter_data  # Сохраняем обработанные данные в сессию

        # Перенаправление на страницу с результатами фильтрации
        return redirect('bike_rental')  # Используем существующий маршрут

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
    results = list(BikeBrand.objects.filter(name__icontains=query).values_list('name', flat=True))
    results += list(BikeModel.objects.filter(Q(model__icontains=query) | Q(brand__name__icontains=query))
                    .annotate(full_name=Concat('brand__name', Value(' '), 'model'))
                    .values_list('full_name', flat=True))
    return JsonResponse(results, safe=False)


