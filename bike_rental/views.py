import random
from datetime import datetime, timedelta
from django.conf import settings
from django_filters.views import FilterView
from django.core.paginator import Paginator
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView
from django.http import JsonResponse
from django.views import View
from tomlkit import comment
from .forms import ClientForm, OrderForm
from .models import Bike, BikeBrand, BikeModel, BikeOrder, BikeType, RidePurpose, BikeProvider, ProviderService, Season, Price, Promouter
from .utils import get_total_bikes_for_brand, calculate_total_price
from django.utils.http import urlencode
from django.views.decorators.http import require_GET
from django.db.models import Min, F, ExpressionWrapper, DecimalField, Count, Min, Q, Value

from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


class BikeModelListView(ListView):
    model = BikeModel
    template_name = "bike_rental.html"
    context_object_name = "bike_rental"
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        today = timezone.now().date()
        
        queryset = queryset.annotate(
            min_price_per_day=ExpressionWrapper(
                Min(F('bikes__prices__cost') / F('bikes__prices__duration')),
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        ).filter(
            bikes__prices__season__start_date__lte=today,
            bikes__prices__season__close_date__gte=today
        ).distinct()

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
                price_filters |= Q(bikes__price_per_day__lte=50)
            elif category == 'Standard':
                price_filters |= Q(bikes__price_per_day__gt=50, bikes__price_per_day__lte=100)
            elif category == 'Premium':
                price_filters |= Q(bikes__price_per_day__gt=100)
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
    if filter_to_remove in current_filters:
        current_filters[filter_to_remove] = [v for v in current_filters[filter_to_remove] if v != value_to_remove]
        if not current_filters[filter_to_remove]:
            del current_filters[filter_to_remove]

    print("Обновленные фильтры:", current_filters)  # Отладка
    request.session['applied_filters'] = current_filters
    return redirect('bike_rental')

    
class BikeFilterView(View):
    """
    Класс-представление для обработки фильтрации байков.
    Сохраняет примененные фильтры в сессии и перенаправляет на страницу результатов.
    """

    def get(self, request, *args, **kwargs):
        print("Данные GET-запроса:", request.GET)  # Отладка: вывод данных GET-запроса
        filter_data = {}
        for key, value in request.GET.items():
            if value:  # Проверяем, что значение не пустое
                filter_data[key] = value.split(',')  # Предполагаем, что параметры могут быть списками

        print("Данные для сохранения в сессию:", filter_data)  # Отладка: что сохраняем в сессию
        print("Примененные фильтры перед сохранением:", filter_data)  # Отладка
        request.session['applied_filters'] = filter_data  # Сохраняем обработанные данные в сессию
        print("Фильтры после сохранения в сессии:", request.session.get('applied_filters'))  # Отладка

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
    today = timezone.now().date()

    def get_prices(date):
        current_season = Season.objects.filter(
            start_date__lte=date,
            close_date__gte=date,
            bike_provider=bike.bike_provider
        ).first()
        return Price.objects.filter(bike=bike) if current_season else Price.objects.none()

    prices = get_prices(today)  # Инициализируем prices до проверки метода

    if request.method == "POST":
        form = OrderForm(request.POST, bike=bike)
        client_form = ClientForm(request.POST)
        
        # Проверяем валидность форм перед доступом к cleaned_data
        if form.is_valid() and client_form.is_valid():
            # Логируем данные формы
            print("Данные формы:", form.cleaned_data)
            print("Данные формы клиента:", client_form.cleaned_data)

            start_date = form.cleaned_data['start_date']
            duration = int(form.cleaned_data['duration'])
            amount_bikes = int(form.cleaned_data['amount_bikes'])
            
            # Логируем значения
            print(f"Start Date: {start_date}, Duration: {duration}, Amount of Bikes: {amount_bikes}")

            prices = get_prices(start_date)  # Обновляем prices на основе выбранной даты
            print("Цены на выбранную дату:", prices)

            if not prices:
                form.add_error('start_date', "No valid prices for the selected date.")
                print("Ошибка: Нет действительных цен для выбранной даты.")
            else:
                total_price = calculate_total_price(duration, amount_bikes, prices)
                print(f"Общая цена: {total_price}")

                if total_price == 0:
                    form.add_error(None, "Error total price calculation.")
                    print("Ошибка: Ошибка расчета общей цены.")
                else:
                    order = BikeOrder(client=client_form.save(), bike=bike, start_date=start_date,
                                      duration=duration, amount_bikes=amount_bikes, total_price=total_price)
                    order.save()
                    print(f"Заказ создан: {order}")
                    return redirect(reverse("order_confirmation", kwargs={"order_id": order.id}))
        else:
            print("Ошибки формы:", form.errors)
            print("Ошибки формы клиента:", client_form.errors)

    else:
        form = OrderForm(bike=bike)
        client_form = ClientForm()

    context = {
        'bike': bike,
        'prices': list(prices.values()),
        'order_form': form,  # Добавляем форму в контекст
        'client_form': client_form,  # Добавляем форму клиента в контекст
    }

    context = add_design_settings(context)
    return render(request, "bike_order.html", context)

# def bike_order(request, id):
#     bike = get_object_or_404(Bike, id=id)
#     promouter_id = request.session.get('promouter_id')
#     promouter = Promouter.objects.filter(id=promouter_id).first() if promouter_id else None
#     # Определяем текущую дату
#     today = timezone.now().date()
    
#     # данные по умолчанию
#     duration = 1
#     amount_bikes = 1
#     start_date = today
#     context = {
#         'bike': bike,
#         'order_form': None,
#         'client_form': None,  # Передаем форму клиента в контекст (удали если не нужно)
#         'total_price': 0,  # Или любое другое значение по умолчанию
#         'current_season': None, #'current_season': current_season,
#         'prices': Price.objects.none(), # Передаем цены в контекст
#     }

#     # Post отправоъляет пользовательские донные
#     if request.method == "POST":
#         form = OrderForm(request.POST, bike=bike, promouter=promouter)
#         client_form = ClientForm(request.POST)  # Создаем форму клиента
#         if form.is_valid() and client_form.is_valid():  # Проверяем обе формы
#             # Расчет total_price
#             duration = form.cleaned_data['duration']
#             amount_bikes = form.cleaned_data['amount_bikes']
#             start_date = form.cleaned_data['start_date']
#             start_date = datetime.strptime(start_date, "%d-%m-%y").date() if start_date else today

#         else:
#             print(form.errors)  # Вывод ошибок формы
#             print(client_form.errors)  # Вывод ошибок формы клиента
#         context['order_form'] = form
#         context['client_form'] = client_form
#     else:
#         # определи curent_season и prices
#         # Находим сезон по дате
#         form = OrderForm(bike=bike, promouter=promouter)
#         client_form = ClientForm()
#         # if form.is_valid() and client_form.is_valid():  # Проверяем обе формы
        
#         # else:
#         #     print (form.errors)
#         context['order_form'] = form
#         context['client_form'] = client_form
    
#     current_season = Season.objects.filter(
#         start_date__lte=start_date,
#         close_date__gte=start_date,
#         bike_provider=bike.bike_provider
#     ).first()
    
#     if not current_season:
#         context['order_form'].add_error('start_date', "No valid current_season for the selected date.")
#     else:
#         context['current_season'] = current_season
#         # Получаем цены для сезона
#         prices = Price.objects.filter(bike=bike, season=current_season)
#         print (prices)
#         print ('hello')
        
#         context['prices'] = list(prices.values())
        
#         total_price = calculate_total_price(start_date, duration, amount_bikes, current_season, prices )
#         if total_price == 0:
#             context['order_form'].add_error(None, "No valid price found.")
#         else:
#             context['total_price'] = total_price
            
#     context = add_design_settings(context)
#     return render(request, "bike_order.html", context)

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
            "%m-%d-%"),
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

def track_promouter(request):
    utm_code = request.GET.get('utm_campaign')
    if utm_code:
        promouter = Promouter.objects.filter(utm_code=utm_code).first()
        if promouter:
            request.session['promouter_id'] = promouter.id
        else:
            request.session['source'] = 'direct'
    
    # Сохраняем источник в куки, если это первое посещение
    if 'first_source' not in request.COOKIES:
        response = redirect('bike_rental')
        response.set_cookie('first_source', request.session['source'], max_age=90*24*60*60)  # 90 дней
        return response

    return redirect('bike_rental')  # Перенаправление на главную страницу