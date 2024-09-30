from django import forms

from .models import BikeOrder, Client, Season, Price, Promouter

ERR_MESSAGE = "Not enough bikes available."


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "contact"]


class OrderForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "DD-MM-YY"}),
        input_formats=["%d-%m-%y"],
    )

    amount_bikes = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 5)],
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    duration = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={
                "type": "range",
                "class": "form-range",
                "min": "1",
                "max": "30",
                "step": "1",
                "id": "customRange3",
                "value": "1",
                "oninput": 'this.style.setProperty("--value", this.value)',
            }
        )
    )

    promouter_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = BikeOrder
        fields = ["start_date", "duration", "amount_bikes"]

    def __init__(self, *args, **kwargs):
        self.bike = kwargs.pop("bike", None)
        self.promouter = kwargs.pop("promouter", None)
        super(OrderForm, self).__init__(*args, **kwargs)
        if self.promouter:
            self.fields['promouter_id'].initial = self.promouter.id

    def save(self, commit=True):
        instance = super().save(commit=False)
        promouter_id = self.cleaned_data.get('promouter_id')
        if promouter_id:
            instance.promouter = Promouter.objects.get(id=promouter_id)
        if commit:
            instance.save()
        return instance

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        duration = cleaned_data.get('duration')
        
        if start_date and duration and self.bike:
            season = Season.objects.filter(
                start_date__lte=start_date,
                close_date__gte=start_date,
                bike_provider=self.bike.bike_provider
            ).first()
            
            if not season:
                raise forms.ValidationError("No valid season for the selected date.")
            
            price = Price.objects.filter(
                bike=self.bike,
                season=season,
                duration=duration
            ).first()
            
            if not price:
                raise forms.ValidationError("No price available for the selected duration and season.")
        
        return cleaned_data