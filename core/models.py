from django.db import models

class Place(models.Model):
    TYPE_CHOICES = [
        ('activity', 'Activity'),
        ('restaurant', 'Restaurant'),
        ('hotel', 'Hotel'),
    ]

    name = models.CharField(max_length = 200)
    country = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)

    type = models.CharField(max_length = 20, choices = TYPE_CHOICES)

    category = models.JSONField()
    price_range = models.IntegerField()

    lat = models.FloatField()
    lng = models.FloatField()

    rating = models.FloatField(null=True, blank=True)

    image = models.URLField() # URLs so no uploading

    duration = models.IntegerField(null = True, blank = True)
    cuisine_type = models.CharField(max_length = 100, null = True, blank = True)
    hotel_stars = models.IntegerField(null = True, blank = True)

    def __str__(self):
        return self.name