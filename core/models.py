from django.db import models
from django.contrib.auth.models import User

# BASE ABSTRACT CLASS
class BasePlace(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    lat = models.FloatField()
    lng = models.FloatField()

    base_price = models.FloatField(default=0)

    rating = models.FloatField(null=True, blank=True)
    image = models.URLField()
    description = models.TextField(default="", blank=True)

    tags = models.CharField(max_length=255, default="", blank=True) # "museum,walk,food"

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def get_location(self):
        return f"{self.city}, {self.country}"

    def get_price(self):
        return self.base_price

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def __str__(self):
        return self.name


# ACTIVITY class
class Activity(BasePlace):
    category = models.CharField(max_length=100)
    duration = models.FloatField(default=1)

    def display_card(self):
        return f"{self.name} | {self.duration}h | ${self.base_price}"


# RESTAURANT class
class Restaurant(BasePlace):
    cuisine_type = models.CharField(max_length=100)
    is_cafe = models.BooleanField(default=False)

    def display_card(self):
        return f"{self.name} ({self.cuisine_type}) | ${self.base_price}"


# HOTEL class
class Hotel(BasePlace):
    stars = models.IntegerField(default=3)

    def get_min_room_price(self):
        return self.base_price

    def display_card(self):
        return f"{self.name} ⭐{self.stars} | from ${self.base_price}"
    

class SavedPlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # generic linking
    place_type = models.CharField(max_length=20) # tivity/restaurant/hotel
    place_id = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} saved {self.place_type}:{self.place_id}"