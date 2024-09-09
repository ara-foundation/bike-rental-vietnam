from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class TourDate(models.Model):
    date = models.DateField()

    def __str__(self):
        return str(self.date)


class Lunch(models.Model):
    name = models.CharField(max_length=50)
    ingredients = models.TextField()

    def __str__(self):
        return self.name


class CabinType(models.Model):
    type = models.CharField(max_length=50)
    description = models.TextField()
    photo = models.ImageField(upload_to="cabins/", blank=True)

    def __str__(self):
        return self.description


class Ship(models.Model):
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=50)
    description = models.TextField()
    photo = models.ImageField(upload_to="images/", blank=True)
    amount_of_places = models.IntegerField()
    cabin_types = models.ForeignKey("CabinType", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Route(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    photo = models.ManyToManyField("Photo", blank=True)
    duration = models.DurationField()

    def __str__(self):
        return self.name


class FreeOfChargeService(models.Model):
    service_name = models.CharField(max_length=50, default="Default Service")
    service_description = models.TextField(blank=True, default="Default Description")

    def __str__(self):
        return self.service_name


class AdditionalOption(models.Model):
    option_name = models.CharField(max_length=50, default="Default Option")
    option_description = models.TextField(blank=True, default="Default Description")

    def __str__(self):
        return self.option_name


class Photo(models.Model):
    image = models.ImageField(upload_to="tours/gallery/")
    description = models.TextField(blank=True, default="Default Description")

    def __str__(self):
        return self.description


class Tour(models.Model):
    name = models.CharField(max_length=50)
    tour_description = models.TextField()
    tour_photo_gallery = models.ManyToManyField("Photo", blank=True)
    route = models.ManyToManyField("Route", blank=True)
    ship = models.ForeignKey("Ship", on_delete=models.SET_NULL, null=True, blank=True)
    lunch = models.ManyToManyField("Lunch", blank=True)
    start_date = models.ForeignKey(
        "TourDate", on_delete=models.SET_NULL, null=True, blank=True
    )
    duration = models.DurationField()
    pick_up_time = models.TimeField()
    free_services = models.ManyToManyField("FreeOfChargeService", blank=True)
    additional_options = models.ManyToManyField("AdditionalOption", blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    cost_options = models.TextField(blank=True, default="Default Cost Options")
    author = models.ForeignKey(User, on_delete=models.CASCADE)  # For roles segregation

    def __str__(self):
        return self.name


class TourOrder(models.Model):
    tour = models.ForeignKey("Tour", on_delete=models.CASCADE, related_name="orders")
    passengers = models.TextField()
    date = models.DateField(default=timezone.now)
    email_of_initiator = models.EmailField()
    phone_number = models.CharField(max_length=50)
    messenger = models.CharField(max_length=50)
    cost_per_person = models.DecimalField(max_digits=10, decimal_places=2)
    cost_of_tour = models.DecimalField(max_digits=10, decimal_places=2)
    name_of_tour = models.TextField()
    duration_of_tour = models.DurationField()
    status = models.BooleanField(default=False)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name_of_tour
