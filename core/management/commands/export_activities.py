import json
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Activity # Ensure this matches your app name (trevia or core)

class Command(BaseCommand):
    help = 'Export activities from Database to activities.json'

    def handle(self, *args, **kwargs):
        json_path = settings.BASE_DIR / 'static' / 'data' / 'activities.json'
        
        # Get all activities from the database
        activities = Activity.objects.all().order_by('id')
        
        data_list = []
        for a in activities:
            data_list.append({
                "id": a.id,
                "name": a.name,
                "country": a.country,
                "city": a.city,
                "category": a.category if hasattr(a, 'category') else [], # Handle if category is a list
                "duration": float(a.duration) if a.duration else 0,
                "price": float(a.price) if a.price else 0,
                "lat": float(a.lat) if a.lat else 0,
                "lng": float(a.lng) if a.lng else 0,
                "image": a.image, # This will now be the NEW Pexels URL
                "description": a.description
            })

        # Write to JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data_list, f, indent=4, ensure_ascii=False)
        
        self.stdout.write(self.style.SUCCESS(f'Successfully updated {len(data_list)} items in activities.json'))