import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Hotel

class Command(BaseCommand):
    help = 'Sync hotels images from JSON file'

    def handle(self, *args, **kwargs):
        # 1. Ensure we are pointing to the correct file
        json_path = settings.BASE_DIR / 'static' / 'data' / 'hotels.json'
        
        self.stdout.write(f'Looking for: {json_path}')

        if not json_path.exists():
            self.stdout.write(self.style.ERROR(f'File not found at: {json_path}'))
            return

        with open(json_path, encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                self.stdout.write(self.style.ERROR('Failed to decode JSON. Check for syntax errors.'))
                return

        # 2. Access the list inside the "hotels" key
        # If your JSON is { "hotels": [...] }, this gets that list.
        hotel_list = data.get('hotels', [])

        if not isinstance(hotel_list, list):
            self.stdout.write(self.style.ERROR('Expected a list of hotels, but got something else.'))
            return

        updated = 0
        for item in hotel_list:
            # 3. Defensive check: Ensure 'name' and 'image' exist in the current item
            name = item.get('name')
            image_url = item.get('image')

            if name and image_url:
                rows = Hotel.objects.filter(name=name).update(image=image_url)
                updated += rows
            else:
                self.stdout.write(self.style.WARNING(f"Skipping entry missing 'name' or 'image': {item}"))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} hotels'))