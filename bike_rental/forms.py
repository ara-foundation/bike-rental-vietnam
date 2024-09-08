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
    
    amount_bikes = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],  # Create a list of choices from 1 to 4
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    
    
    duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'type': 'range',
            'class': 'form-range',
            'min': '1',
            'max': '30',
            'step': '1',
            'id': 'customRange3',
            'value': '1',  # Adding default value
            'oninput': 'this.style.setProperty("--value", this.value)'
        })
    )
    
    class Meta:
        model = Order
        fields = ['start_date', 'duration', 'amount_bikes']

    def __init__(self, *args, **kwargs):
        self.bike = kwargs.pop('bike', None)
        super(OrderForm, self).__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        amount_bikes = int(cleaned_data.get('amount_bikes'))
        if self.bike and amount_bikes > self.bike.amount:
            raise forms.ValidationError("Not enough bikes available.")
        return cleaned_data