from django.db import models

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

    class Meta:
        ordering = ['brand__name', 'model']
        verbose_name = 'Bike Model'
        verbose_name_plural = 'Bike Models'

    def __str__(self):
        return f"{self.brand.name} {self.model}"


class Bike(models.Model):
    bike_model = models.ForeignKey(BikeModel, on_delete=models.PROTECT, related_name='bikes')
    deposit_amount = models.IntegerField()
    amount = models.IntegerField()
    availability = models.BooleanField(default=True)
    photos = models.ImageField(upload_to='images/', null=True, blank=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.bike_model} - {self.amount} available"
