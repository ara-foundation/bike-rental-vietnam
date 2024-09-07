import django_filters
from .models import BikeModel, BikeBrand

class BikeModelFilter(django_filters.FilterSet):
    brand = django_filters.ModelChoiceFilter(
        queryset=BikeBrand.objects.all(),
        label="Brand",
        empty_label="All brands"
    )
    model = django_filters.ModelChoiceFilter(
        queryset=BikeModel.objects.none(),
        label="Model",
        empty_label="All models"
    )
    transmission = django_filters.ChoiceFilter(
        choices=[],
        label="Transmission",
        empty_label="All transmissions"
    )

    class Meta:
        model = BikeModel
        fields = ['brand', 'model', 'transmission']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'brand' in self.data:
            try:
                brand_id = int(self.data['brand'])
                self.filters['model'].queryset = BikeModel.objects.filter(brand_id=brand_id)
            except (ValueError, TypeError):
                pass
        if 'model' in self.data:
            try:
                model_id = int(self.data['model'])
                self.filters['transmission'].choices = BikeModel.objects.filter(id=model_id).values_list('transmission', 'transmission').distinct()
            except (ValueError, TypeError):
                pass