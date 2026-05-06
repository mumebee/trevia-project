from django.db import models
from django.contrib.auth.models import User


class BasePlace(models.Model):
    name = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    lat = models.FloatField()
    lng = models.FloatField()

    price = models.FloatField(default=0)
    rating = models.FloatField(null=True, blank=True)

    image = models.URLField()
    description = models.TextField(default="", blank=True)

    tags = models.CharField(max_length=255, default="", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


    def get_location(self):
        return f"{self.city}, {self.country}"

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]

    def get_price(self):
        return self.price

    def __str__(self):
        return self.name


class Activity(BasePlace):
    category = models.JSONField(default=list)
    duration = models.FloatField(default=1)

    def save(self, *args, **kwargs):
        # Automatically sync the category list to the tags string for filtering
        if isinstance(self.category, list):
            self.tags = ",".join(str(cat).strip().lower() for cat in self.category)
        super().save(*args, **kwargs)

    def display_card(self):
        return f"{self.name} | {self.duration}h | ${self.price}"



class Restaurant(BasePlace):
    cuisine_type = models.CharField(max_length=100)
    menu = models.JSONField(default=dict)

    def display_card(self):
        return f"{self.name} ({self.cuisine_type}) | ${self.price}"


class Hotel(BasePlace):
    stars = models.IntegerField(default=3)

    # KEEP YOUR JSON DATA
    rooms = models.JSONField(default=list)
    food = models.JSONField(default=list)
    reviews = models.JSONField(default=dict)
    image = models.URLField(blank=True, null=True)

    def get_min_room_price(self):
        if not self.rooms:
            return self.price
        return min(room.get("price", self.price) for room in self.rooms)

    def display_card(self):
        return f"{self.name} ⭐{self.stars} | from ${self.get_min_room_price()}"
    # karimaf 
    def save(self, *args, **kwargs):
        if self.rooms:
         self.price = self.get_min_room_price()
        super().save(*args, **kwargs)

class SavedPlace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place_type = models.CharField(max_length=20)
    place_id = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)


class Itinerary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} ({self.user})"


class ItineraryItem(models.Model):
    itinerary = models.ForeignKey(Itinerary, on_delete=models.CASCADE)
    place_type = models.CharField(max_length=20)
    place_id = models.IntegerField()
    order = models.IntegerField()

    def __str__(self):
        return f"{self.place_type}:{self.place_id} -> {self.itinerary.name}"