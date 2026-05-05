import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Restaurant


class Command(BaseCommand):
    help = 'Sync restaurants images from JSON file'

    def handle(self, *args, **kwargs):
        json_path = settings.BASE_DIR / 'static' / 'data' / 'restaurants.json'
        
        self.stdout.write(f'Looking for: {json_path}')

        with open(json_path, encoding='utf-8') as f:
            data = json.load(f)

        updated = 0
        for item in data:
            rows = Restaurant.objects.filter(name=item['name']).update(image=item['image'])
            updated += rows

        self.stdout.write(self.style.SUCCESS(f'Updated {updated} restaurants'))