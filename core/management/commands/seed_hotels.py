import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Hotel

class Command(BaseCommand):
    help = 'Seeds the database with hotel data from hotels.json'
    location = hotel_data.get('location', {})

    def handle(self, *args, **options):
        # Update path to where your JSON file is located
        json_path = settings.BASE_DIR / 'static' / 'data' / 'hotels.json'

        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            # CRITICAL FIX: Iterate over data['hotels']
            hotels_list = data

            for hotel_data in hotels_list:
                # 1. Create or Update the Hotel
                hotel, created = Hotel.objects.update_or_create(
                    name=hotel_data['name'],
                    defaults={
                        'country': hotel_data['country'],
                        'city': hotel_data['city'],
                        'image_url': hotel_data['image'],
                        'latitude': hotel_data['location']['lat'],
                        'longitude': hotel_data['location']['long'],
                        'good_reviews': "\n".join(hotel_data['views']['good']),
                        'bad_reviews': "\n".join(hotel_data['views']['bad']),
                    }
                )

                # 2. Seed Rooms for this Hotel
                for room_data in hotel_data.get('rooms', []):
                    Room.objects.get_or_create(
                        hotel=hotel,
                        name=room_data['name'],
                        defaults={
                            'size': room_data['size'],
                            'beds': room_data['beds'],
                            'price': room_data['price']
                        }
                    )

                # 3. Seed Food/Dining for this Hotel
                for food_data in hotel_data.get('food', []):
                    # Joining menu items into a string if your model uses a TextField
                    menu_items = ", ".join(food_data['menu'])
                    Food.objects.get_or_create(
                        hotel=hotel,
                        place_name=food_data['place_name'],
                        defaults={
                            'menu': menu_items,
                            # Assuming you store average or specific prices
                            'price_range': str(food_data['price']) 
                        }
                    )

                self.stdout.write(self.style.SUCCESS(f'Successfully seeded "{hotel.name}"'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found at {json_path}'))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'Missing expected key in JSON: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {e}'))