import json
from core.models import Activity, Restaurant, Hotel


def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run():
    # ACTIVITIES
    activities = load_json("data/activities.json")
    for item in activities:
        Activity.objects.create(
            name =item["name"],
            country = item["country"],
            city = item["city"],
            category = item.get("category", []),
            duration = item.get("duration", 1),
            price = item["price"],
            lat = item["lat"],
            lng = item["lng"],
            image = item["image"]
        )

    # RESTAURANTS
    restaurants = load_json("data/restaurants.json")
    for item in restaurants:
        Restaurant.objects.create(
            name = item["name"],
            country = item["country"],
            city = item["city"],
            cuisine_type = item.get("cuisine_type", ""),
            price = item["price"],
            lat = item["lat"],
            lng = item["lng"],
            image = item["image"]
        )

    # HOTELS
    hotels = load_json("data/hotels.json")
    for item in hotels:
        Hotel.objects.create(
            name = item["name"],
            country = item["country"],
            city = item["city"],
            stars = item.get("stars", 3),
            price = item["price"],
            lat = item["lat"],
            lng = item["lng"],
            image = item["image"]
        )

    print("DATA IMPORTING COMPLETE!!!")