from django.db import models


# ABSTRACT BASE CLASS

class BasePlace(models.Model):
    name = models.CharField(max_length = 200)
    country = models.CharField(max_length = 100)
    city = models.CharField(max_length = 100)

    lat = models.FloatField()
    lng = models.FloatField()

    # real price in USD
    price = models.FloatField(help_text = "Price in USD")

    rating = models.FloatField(null = True, blank = True)
    image = models.URLField()

    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        abstract = True

    # encapsulation with method to get location
    def get_location(self):
        return f"{self.city}, {self.country}"

    # polymorphism to display card info, overriden in child classes
    def display_card(self):
        return f"{self.name} - ${self.price}"

    def __str__(self):
        return self.name

"""
CHILD CLASSES FROM ABSTRACT BASE CLASS BasePlace
shows inheritance
"""

# ACTIVITY MODEL
class Activity(BasePlace):
    category = models.JSONField()  # ["museum", "nature"]
    duration = models.IntegerField(help_text = "Duration in hours")

    # polymorphism with adding category and duration
    def display_card(self):
        return f"{self.name}: - {self.duration}h - ${self.price}"


# RESTAURANT MODEL
class Restaurant(BasePlace):
    cuisine_type = models.CharField(max_length=100)
    is_cafe = models.BooleanField(default = False)

    # polymorphism with adding cuisine type
    def display_card(self):
        return f"{self.name}: ({self.cuisine_type}) - ${self.price}"


# HOTEL MODEL
class Hotel(BasePlace):
    stars = models.IntegerField(help_text = "1–5 stars")

    # polymorphism with adding stars
    def display_card(self):
        return f"{self.name} ⭐{self.stars} - ${self.price}/night"