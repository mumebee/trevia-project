import json
from django.conf import settings
from django.core.management.base import BaseCommand
from core.models import Hotel

class Command(BaseCommand):
    help = 'Imports hotels from a JSON file'

    def handle(self, *args, **options):
        # Path to your json data
        data_path = settings.BASE_DIR / 'static' / 'data' / 'hotels.json'
        
        with open(data_path, 'r', encoding='utf-8') as f:
            restaurants_data = json.load(f)

        for item in restaurants_data:
            obj, created = Hotel.objects.get_or_create(
                name=item['name'],
                defaults={
                    'country': item['country'],
                    'city': item['city'],
                    'lat': item.get('lat'),
                    'lng': item.get('lng'),
                    'image': item.get('image', ''),
                    'cuisine_type': item.get('cuisine_tags', [''])[0],
                    'tags': item.get('cuisine_tags', []),
                    'menu': item.get('menu', {}),
                    'price': 0, 
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created {obj.name}"))
            else:
                self.stdout.write(f"{obj.name} already exists.")