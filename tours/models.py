from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class TourDate(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE,
                             related_name='tour_dates')
    date = models.DateField()

    def __str__(self):
        return f"{self.tour.name} - {self.date}"


class FreeOfChargeService(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE,
                             related_name='free_services')
    service_description = models.TextField()

    def __str__(self):
        return f"{self.tour.name} - Free Service: {self.service_description[:50]}"


class AdditionalOption(models.Model):
    tour = models.ForeignKey('Tour', on_delete=models.CASCADE,
                             related_name='additional_options')
    option_name = models.CharField(max_length=255)
    option_description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.tour.name} - Option: {self.option_name}"


class Photo(models.Model):
    image = models.ImageField(upload_to='tours/gallery/')
    description = models.TextField(blank=True, null=True)


class Tour(models.Model):
    name = models.CharField(max_length=255)
    tour_description = models.TextField()
    tour_photo_gallery = models.ManyToManyField('Photo', blank=True)
    duration = models.DurationField()
    pick_up_time = models.TimeField()
    cost = models.DecimalField(max_digits=10,
                               decimal_places=2)
    cost_options = models.TextField(blank=True,
                                    null=True)

    def __str__(self):
        return self.name
