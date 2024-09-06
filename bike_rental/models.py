from django.db import models
from django.core.validators import MinValueValidator

class BikeBrand(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class BikeModel(models.Model):
    brand = models.ForeignKey(BikeBrand, on_delete=models.PROTECT, related_name='models')
    model = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    gears = models.IntegerField(null=True, blank=True)
    displacement = models.FloatField()
    fuel_system = models.CharField(max_length=255, default="carburettor")  # Значение по умолчанию
    tank = models.FloatField(default=0)  # Значение по умолчанию
    clearance = models.IntegerField()
    description = models.TextField()
    bike_model_photo = models.ImageField(upload_to='bike_model_photos/', null=True, blank=True)

    class Meta:
        ordering = ['brand__name', 'model']
        verbose_name = 'Bike Model'
        verbose_name_plural = 'Bike Models'

    def __str__(self):
        return f"{self.brand.name} {self.model}"


class Bike(models.Model):
    bike_model = models.ForeignKey(BikeModel, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='bike_photos/', null=True, blank=True)  # Изменено с 'images/' на 'bike_photos/'
    deposit_amount = models.IntegerField()
    amount = models.IntegerField()
    availability = models.BooleanField(default=True)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)

    def __str__(self):
        return f"{self.bike_model} - {self.amount} available"


class Client(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='orders')
    bike = models.ForeignKey(Bike, on_delete=models.PROTECT, related_name='orders')
    start_date = models.DateField()
    duration = models.IntegerField(validators=[MinValueValidator(1)])
    amount_bikes = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.client.name}"
