import json
from core.models import Activity, Restaurant, Hotel


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ACTIVITIES
def import_activities():
    data = load_json("data/activities.json")

    for item in data:
        Activity.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            category=item.get("category", ["general"])[0],
            duration=item.get("duration", 1),
            base_price=item.get("price", 0),
            lat=item["lat"],
            lng=item["lng"],
            image=item["image"],
            tags=",".join(item.get("category", []))
        )


# RESTAURANTS
def import_restaurants():
    data = load_json("data/restaurants.json")

    for item in data:
        Restaurant.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            cuisine_type=item.get("cuisine_type", ""),
            base_price=item.get("price", 0),
            lat=item["lat"],
            lng=item["lng"],
            image=item["image"],
            tags=item.get("cuisine_type", "")
        )


# HOTELS
def import_hotels():
    data = load_json("data/hotels.json")["hotels"]

    for item in data:
        min_price = min(room["price"] for room in item.get("rooms", []))

        Hotel.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            stars=3,
            base_price=min_price,
            lat=item["location"]["lat"],
            lng=item["location"]["long"],
            image="https://via.placeholder.com/300",
            tags="hotel,luxury"
        )


def run():
    import_activities()
    import_restaurants()
    import_hotels()
    print("DATA IMPORT COMPLETE")