from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TourDate(models.Model):
    date = models.DateField()

    def __str__(self):
        return str(self.date)


class FreeOfChargeService(models.Model):
    service_name = models.CharField(max_length=50, default="Default Service")
    service_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.service_name


class AdditionalOption(models.Model):
    option_name = models.CharField(max_length=50, default="Default Option")
    option_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.option_name


class Photo(models.Model):
    image = models.ImageField(upload_to='tours/gallery/')
    description = models.TextField(blank=True, null=True)


class Tour(models.Model):
    name = models.CharField(max_length=255)
    tour_description = models.TextField()
    tour_photo_gallery = models.ManyToManyField('Photo', blank=True)
    dates = models.ManyToManyField('TourDate', blank=True)
    duration = models.DurationField()
    pick_up_time = models.TimeField()
    free_services = models.ManyToManyField('FreeOfChargeService', blank=True)
    additional_options = models.ManyToManyField('AdditionalOption', blank=True)
    cost = models.DecimalField(max_digits=10,
                               decimal_places=2)
    cost_options = models.TextField(blank=True,
                                    null=True)

    def __str__(self):
        return self.name
