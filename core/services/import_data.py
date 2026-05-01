import json
from pathlib import Path
from django.conf import settings
from core.models import Activity, Restaurant, Hotel


def load_json(filename):
    path = Path(settings.BASE_DIR) / "static" / "data" / filename
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ACTIVITIES

def import_activities():
    data = load_json("activities.json")

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
            description=item.get("description", ""),
            tags=",".join(item.get("category", []))
        )


# RESTAURANTS
def import_restaurants():
    data = load_json("restaurants.json")

    for item in data:
        avg_price = sum(item["menu"].values()) / len(item["menu"])

        Restaurant.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            cuisine_type=item.get("cuisine_type", ""),
            base_price=avg_price,
            lat=item["lat"],
            lng=item["lng"],
            image=item["image"],
            menu=item.get("menu", {}),
            tags=item.get("cuisine_type", "")
        )

# HOTELS
def import_hotels():
    data = load_json("hotels.json")["hotels"]

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
            rooms=item.get("rooms", []),
            food=item.get("food", []),
            reviews=item.get("views", {}),
            tags="hotel"
        )


def run():
    import_activities()
    import_restaurants()
    import_hotels()
    print("DATA IMPORT COMPLETE")