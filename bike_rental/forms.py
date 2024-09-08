from django import forms
from .models import Order, Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'contact']

class OrderForm(forms.ModelForm):
    start_date = forms.DateField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'DD-MM'}),
        input_formats=['%d-%m']
    )
    
    class Meta:
        model = Order
        fields = ['start_date', 'duration', 'amount_bikes']

    def __init__(self, *args, **kwargs):
        self.bike = kwargs.pop('bike', None)
        super(OrderForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount_bikes = cleaned_data.get('amount_bikes')
        if self.bike and amount_bikes > self.bike.amount:
            raise forms.ValidationError("Not enough bikes available.")
        return cleaned_data
        return cleaned_data