from django.db import models


# ABSTRACT BASE CLASS
class BasePlace(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    lat = models.FloatField()
    lng = models.FloatField()

    min_price = models.FloatField(default=0)
    max_price = models.FloatField(default=0)

    rating = models.FloatField(null=True, blank=True)
    image = models.URLField()
    description = models.TextField(default="", blank=True)

    tags = models.CharField(max_length=200, default="", blank=True) # "museum,walk,food"

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    # encapsulation for ze prof
    def get_location(self):
        return f"{self.city}, {self.country}"

    # shared price display
    def get_price_range(self):
        return f"${self.min_price} - ${self.max_price}"

    def __str__(self):
        return self.name


# ACTIVITY MODEL
class Activity(BasePlace):
    category = models.CharField(max_length=50) # "culture", "nature"
    duration = models.FloatField(default=1)

    # polymorphism
    def display_card(self):
        return f"{self.name} | {self.duration}h | {self.get_price_range()}"


# RESTAURANT MODEL
class Restaurant(BasePlace):
    cuisine_type = models.CharField(max_length=100)
    is_cafe = models.BooleanField(default=False)

    def display_card(self):
        return f"{self.name} ({self.cuisine_type}) | {self.get_price_range()}"


# HOTEL MODEL
class Hotel(BasePlace):
    stars = models.IntegerField(help_text="1–5 stars")

    def display_card(self):
        return f"{self.name} ⭐{self.stars} | {self.get_price_range()}"