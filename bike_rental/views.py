from datetime import UTC, datetime

from django.conf import settings
from django.db.models import Count, Min
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import ListView

from .forms import ClientForm, OrderForm
from .models import Bike, BikeBrand, BikeModel, BikeOrder


class BikeModelListView(ListView):
    model = BikeModel
    template_name = "bikemodel_list.html"
    context_object_name = "bikemodels"
    paginate_by = 9

    def get_queryset(self):
        # Now each query set contains additional fields bikes_count, min_price
        # and suppliers_count.
        # These can be accessed in template like this: {{ bikemodel.bikes_count }}
        # {{ bikemodel.min_price }} and {{ bikemodel.suppliers_count }}
        queryset = BikeModel.objects.annotate(
            bikes_count=Count("bikes"),  # Count of bikes associated with the BikeModel
            min_price=Min("bikes__price_per_day"),  # Minimum price per day of
            # associated bikes
            suppliers_count=Count("bikes__owner", distinct=True),
            # Count of distinct owners (suppliers)
        )
        brand = self.request.GET.get("brand")
        transmission = self.request.GET.get("transmission")

        if brand:
            queryset = queryset.filter(brand_id=brand)
        if transmission:
            queryset = queryset.filter(transmission=transmission)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["brands"] = BikeBrand.objects.all()
        context["transmissions"] = BikeModel.objects.values_list(
            "transmission", flat=True
        ).distinct()

        selected_brand_id = self.request.GET.get("brand")
        if selected_brand_id:
            context["selected_brand"] = int(selected_brand_id)
            context["selected_brand_name"] = BikeBrand.objects.get(
                id=selected_brand_id
            ).name
        else:
            context["selected_brand"] = None

        context["selected_transmission"] = self.request.GET.get("transmission")
        if context["selected_brand"]:
            context["selected_brand_name"] = BikeBrand.objects.get(
                id=context["selected_brand"]
            ).name
        context["bikemodels_count"] = self.get_queryset().count()
        return add_design_settings(context)


def bikemodel_detail(request, id):
    bikemodel = get_object_or_404(BikeModel, id=id)
    bikes = Bike.objects.filter(bike_model=bikemodel)
    context = {"bikemodel": bikemodel, "bikes": bikes}
    context = add_design_settings(context)
    return render(request, "bikemodel_detail.html", context)


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

            # Добавляем текущий год к дате
            start_date = order_form.cleaned_data["start_date"]
            current_year = datetime.now(UTC).year
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
    # Implement your pricing logic here
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
