import json
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Activity  # Import from your 'core' app

class Command(BaseCommand):
    help = 'Fetches high-quality images from Pexels API and saves them to the database'

    def handle(self, *args, **kwargs):
        # --- CONFIGURATION ---
        # Replace with your actual key from https://www.pexels.com/api/
        PEXELS_API_KEY = 'YOUR_ACTUAL_PEXELS_API_KEY'
        json_path = settings.BASE_DIR / 'static' / 'data' / 'activities.json'
        # ---------------------

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found at {json_path}"))
            return

        headers = {"Authorization": PEXELS_API_KEY}
        self.stdout.write(self.style.SUCCESS(f"Found {len(data)} items. Starting Pexels search..."))

        for item in data:
            name = item.get('name')
            city = item.get('city', 'Uzbekistan')
            
            # Skip if we already have a real image link to save time/quota
            if item.get('image') and "pexels" in item.get('image'):
                continue

            query = f"{name} {city}"
            self.stdout.write(f"Searching: {query}...")

            try:
                # 1. Hit the Pexels API
                url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
                response = requests.get(url, headers=headers)
                
                new_image_url = item.get('image') # Fallback to original

                if response.status_code == 200:
                    results = response.json().get('photos')
                    if results:
                        new_image_url = results[0]['src']['large']
                        self.stdout.write(self.style.SUCCESS(f"  [OK] Found image"))
                    else:
                        self.stdout.write(self.style.WARNING(f"  [EMPTY] No photo on Pexels"))
                
                elif response.status_code == 429:
                    self.stdout.write(self.style.ERROR("Pexels Rate limit hit! Waiting 60s..."))
                    time.sleep(60)

                # 2. Update or Create in Database
                Activity.objects.update_or_create(
                    name=name,
                    defaults={
                        'country': item.get('country'),
                        'city': item.get('city'),
                        'duration': item.get('duration'),
                        'price': item.get('price'),
                        'lat': item.get('lat'),
                        'lng': item.get('lng'),
                        'image': new_image_url,
                        'description': item.get('description'),
                    }
                )
                
                # Small delay to keep the API happy
                time.sleep(0.5)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {name}: {e}"))

        self.stdout.write(self.style.SUCCESS("Finished populating database!"))