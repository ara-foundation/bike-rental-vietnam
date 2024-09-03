import django_filters
from .models import BikeModel, BikeBrand

class BikeModelFilter(django_filters.FilterSet):
    # Фильтр по бренду
    brand = django_filters.ModelChoiceFilter(
        queryset=BikeBrand.objects.all(),
        to_field_name='name',
        field_name='brand',
        lookup_expr='exact',
        label="Brand",
        empty_label="All"
    )

    # Фильтр по модели байка с выпадающим списком
    model = django_filters.ModelChoiceFilter(
        queryset=BikeModel.objects.values_list('model', flat=True).order_by('model').distinct(),
        label="Model",
        to_field_name='model',
        field_name='model',
        empty_label="All"
    )

    # Фильтр по трансмиссии с выпадающим списком
    transmission = django_filters.ModelChoiceFilter(
        queryset=BikeModel.objects.values_list('transmission', flat=True).order_by('transmission').distinct(),
        label="Transmission",
        to_field_name='transmission',
        field_name='transmission',
        empty_label="All"
    )

    class Meta:
        model = BikeModel
        fields = ['brand', 'model', 'transmission']
        order_by = ['brand__name', 'model']