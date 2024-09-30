from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.forms import ValidationError
import datetime
import uuid
import qrcode
import io

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

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

class BikeProvider(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=255)
    contract = models.CharField(max_length=255)
    working_hours = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Bike(models.Model):
    bike_model = models.ForeignKey(
        BikeModel, on_delete=models.PROTECT, related_name="bikes"
    )
    photo = models.ImageField(
        upload_to="bike_photos/", null=True, blank=True
    )
    date_production = models.DateField(default=datetime.date(2015, 1, 1))
    deposit_type = models.CharField(max_length=100)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.IntegerField()
    availability = models.BooleanField(default=True)
    description = models.TextField()
    bike_provider = models.ForeignKey(BikeProvider, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.bike_model} - {self.amount} available"

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
    source = models.CharField(max_length=50, blank=True, null=True)
    first_source = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        # Получаем сессию из kwargs
        session = kwargs.pop('session', None)
        print("Session data:", session)  # Добавьте эту строку для отладки
        if session:
            if not self.source:
                self.source = session.get('source', 'unknown')
            if not self.first_source:
                self.first_source = session.get('first_source', 'unknown')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.client.name}"





class ProviderService(models.Model):
    name = models.CharField(max_length=255)
    availability = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    provider = models.ForeignKey(BikeProvider, on_delete=models.CASCADE, related_name='services')

    def __str__(self):
        return f"{self.name} - {self.provider.name}"

class Season(models.Model):
    SEASON_NAMES = [
        ('High', 'High season'),
        ('Normal', 'Normal season'),
        ('Low', 'Low season'),
    ]
    name = models.CharField(max_length=100, choices=SEASON_NAMES)
    start_date = models.DateField()
    close_date = models.DateField()
    bike_provider = models.ForeignKey('BikeProvider', on_delete=models.CASCADE, related_name='seasons')

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.close_date})"

    def clean(self):
        if self.start_date and self.close_date and self.start_date > self.close_date:
            raise ValidationError(_('Start date must be before close date.'))

    class Meta:
        ordering = ['start_date']

class Price(models.Model):
    DURATION_PRISES = [
        (1, '1 day'),
        (2, '2 days'),
        (3, '3 days'),
        (4, '4 days'),
        (5, '5 days'),
        (6, '7 days'),
        (7, '1 week'),
        (14, '2 weeks'),
        (21, '3 weeks'),
        (30, '1 month'),
    ]
    
    bike = models.ForeignKey(Bike, on_delete=models.CASCADE, related_name='prices')
    season = models.ForeignKey(Season, on_delete=models.CASCADE, null=True, blank=True)
    duration = models.IntegerField(choices=DURATION_PRISES, validators=[MinValueValidator(1)], default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        season_name = self.season.name if self.season else "No season"
        return f"Price for {self.bike} - {season_name} - {self.duration} days"

    class Meta:
        unique_together = ('bike', 'season', 'duration')
        ordering = ['bike', 'season', 'duration']
        
class Promouter(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='promouter_profile')
    promo_pyte = models.CharField(max_length=255, blank=True, null=True)
    comition_percent = models.DecimalField(max_digits=5, decimal_places=2)
    utm_code = models.CharField(max_length=50, unique=True, blank=True, null=True)
    bike_orders = models.ManyToManyField('BikeOrder', related_name='promouters', blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.id}"

    def generate_utm_url(self, base_url):
        return f"{base_url}?utm_source=promouter&utm_medium=referral&utm_campaign={self.utm_code}"

    def generate_unique_utm_code(self):
        code = str(uuid.uuid4())[:8]  # Используем первые 8 символов UUID для краткости
        while Promouter.objects.filter(utm_code=code).exists():
            code = str(uuid.uuid4())[:8]
        return code

    def save(self, *args, **kwargs):
        # Генерация уникального UTM-кода, если он отсутствует
        if not self.utm_code:
            self.utm_code = self.generate_unique_utm_code()
            super().save(*args, **kwargs)  # Сохранение промоутера с новым utm_code

        # Генерация UTM URL
        base_url = "http://127.0.0.1:8000/track/"  # Замените на ваш базовый URL
        utm_url = self.generate_utm_url(base_url)

        # Генерация QR-кода
        qr = qrcode.make(utm_url)
        buffer = io.BytesIO()
        qr.save(buffer, format='PNG')
        qr_filename = f'qr_codes/promouter_{self.id}_{self.utm_code}.png'
        qr_file = ContentFile(buffer.getvalue(), qr_filename)

        # Сохранение QR-кода в медиа-хранилище и создание записи в модели QRCode
        saved_path = default_storage.save(qr_filename, qr_file)
        QRCode.objects.create(
            promouter=self,
            qr_link=utm_url,
            image=saved_path
        )

        super().save(*args, **kwargs)  # Сохранение промоутера без обновления qr_codes

class QRCode(models.Model):
    promouter = models.ForeignKey(Promouter, on_delete=models.CASCADE, related_name='qr_codes')
    qr_link = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='qr_codes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QR Code for {self.promouter.user.username} - {self.id}"