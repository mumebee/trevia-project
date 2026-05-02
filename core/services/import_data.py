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
            category=item.get("category", []),
            duration=item.get("duration", 1),
            price=item.get("price", 0),
            lat=item["lat"],
            lng=item["lng"],
            image=item["image"],
            description=item.get("description", ""),
            tags=",".join(item.get("category", []))
        )


# RESTAURANTS
def import_restaurants():
    data = load_json("restaurants.json") or []

    for item in data:
        menu = item.get("menu", {})
        avg_price = sum(menu.values()) / len(menu) if menu else 0

        Restaurant.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            cuisine_type=item.get("cuisine_type", ""),
            price=avg_price,
            lat=item["lat"],
            lng=item["lng"],
            image=item["image"],
            menu=item.get("menu", {}),
            tags=item.get("cuisine_type", "")
        )

# HOTELS
def import_hotels():
    raw_data = load_json("hotels.json")
    data = raw_data.get("hotels", []) if raw_data else []

    for item in data:
        rooms = item.get("rooms", [])
        min_price = min(room["price"] for room in rooms) if rooms else item.get("price", 0)

        Hotel.objects.create(
            name=item["name"],
            country=item["country"],
            city=item["city"],
            stars=3,
            price=min_price,
            lat=item.get("location", {}).get("lat", 0),
            lng=item.get("location", {}).get("lng", item.get("location", {}).get("long", 0)),
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