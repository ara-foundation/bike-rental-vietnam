from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

User = get_user_model()


class BikeBrand(models.Model):
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="brand_logos/", null=True, blank=True)

    def __str__(self):
        return self.name


class BikeType(models.Model):
    type = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='bike_types/', null=True, blank=True)
    order = models.IntegerField(default=0)  # Добавьте это поле

    class Meta:
        ordering = ['-order']  # Это обеспечит сортировку по умолчанию

    def __str__(self):
        return self.type


class RidePurpose(models.Model):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to='ridepurpose/', null=True, blank=True)

    def __str__(self):
        return self.name
    
class BikeModel(models.Model):
    brand = models.ForeignKey(
        BikeBrand, on_delete=models.PROTECT, related_name="models"
    )
    model = models.CharField(max_length=255)
    transmission = models.CharField(max_length=255)
    gears = models.IntegerField(null=True, blank=True)
    displacement = models.FloatField()
    tank = models.FloatField(default=0)  # Значение по умолчанию
    fuel_system = models.CharField(
        max_length=255, default="carburettor"
    )  # Значение по умолчанию
    max_speed = models.IntegerField(null=True, blank=True)
    clearance = models.IntegerField()  # Изменено с clearance на clearance
    description = models.TextField()
    bike_model_photo = models.ImageField(
        upload_to="bike_model_photos/", null=True, blank=True
    )
    seat_height = models.IntegerField(null=True, blank=True)
    fuel_consumption = models.FloatField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    bike_type = models.ForeignKey(BikeType, on_delete=models.PROTECT, null=True, blank=True, related_name='bike_models')
    ride_purposes = models.ManyToManyField(RidePurpose, related_name='bike_models', blank=True)

    class Meta:
        ordering = ["brand__name", "model"]
        verbose_name = "Bike Model"
        verbose_name_plural = "Bike Models"

    def __str__(self):
        return f"{self.brand.name} {self.model}"

        # def get_min_price_per_day(self):
    #     bikes = self.bike_set.all()
    #     if bikes:
    #         return min(bike.price_per_day for bike in bikes)
    #     return None

    def get_weight_category(self):
        if self.weight is None:
            return "Unknown"
        elif self.weight <= 120:
            return "Light"
        elif 120 < self.weight <= 180:
            return "Middle"
        else:
            return "Heavy"

    def get_specs_with_icons(self):
        specs = [
            ("transmission", {"value": self.transmission, "icon": "bi-gear"}),
            ("gears", {"value": f"{self.gears} gears", "icon": "bi-gear"}),
            (
                "displacement",
                {"value": f"{self.displacement} cc", "icon": "bi-speedometer2"},
            ),
            ("weight", {"value": f"{self.weight} kg", "icon": "bi-box"}),
            ("fuel_system", {"value": self.fuel_system, "icon": "bi-droplet"}),
            (
                "max_speed",
                {"value": f"{self.max_speed} km/h", "icon": "bi-speedometer"},
            ),
            ("seat_height", {"value": f"{self.seat_height} mm", "icon": "bi-person"}),
            (
                "fuel_consumption",
                {"value": f"{self.fuel_consumption} l/100km", "icon": "bi-lightning"},
            ),
            ("tank", {"value": f"{self.tank} liters", "icon": "bi-droplet-fill"}),
            (
                "clearance",
                {"value": f"{self.clearance} mm", "icon": "bi-arrows-expand"},
            ),
        ]
        return [(k, v) for k, v in specs if v["value"] is not None][:9]

    def get_price_category(self):
        if self.price is None:
            return "Unknown"
        elif self.price <= 50:
            return "Budget"
        elif 50 < self.price <= 100:
            return "Standard"
        else:
            return "Premium"


class Bike(models.Model):
    bike_model = models.ForeignKey(
        BikeModel, on_delete=models.PROTECT, related_name="bikes"
    )
    photo = models.ImageField(
        upload_to="bike_photos/", null=True, blank=True
    )  # Изменено с 'images/' на 'bike_photos/'
    deposit_amount = models.IntegerField()
    amount = models.IntegerField()
    availability = models.BooleanField(default=True)
    description = models.TextField()
    price_per_day = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    price_per_week = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=0, default=0.0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bike_model} - {self.amount} available"

    def calculate_rental_price(self, duration):
        if duration >= 30:
            months = duration // 30
            remaining_days = duration % 30
            price = (months * self.price_per_month) + (
                remaining_days * (self.price_per_day)
            )
        elif duration >= 7:
            weeks = duration // 7
            remaining_days = duration % 7
            price = (weeks * self.price_per_week) + (
                remaining_days * self.price_per_day
            )
        else:
            price = duration * self.price_per_day
        return price


class Client(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class BikeOrder(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="orders")
    bike = models.ForeignKey(Bike, on_delete=models.PROTECT, related_name="orders")
    start_date = models.DateField()
    duration = models.IntegerField(validators=[MinValueValidator(1)])
    amount_bikes = models.IntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.client.name}"


