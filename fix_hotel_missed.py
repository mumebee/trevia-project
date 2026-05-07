import json, time
from ddgs import DDGS

JSON_PATH = 'static/data/hotels.json'
raw = json.load(open(JSON_PATH, encoding='utf-8'))
data = raw['hotels']

MISSED_IDS = {2, 4, 7, 9, 15, 17, 18, 20, 26, 31, 33, 34, 38, 39, 48, 52, 63, 67, 72, 78, 79, 81, 83, 88, 115, 119, 139, 140}

with DDGS() as d:
    for item in data:
        if item['id'] not in MISSED_IDS:
            continue
        query = f"{item['name']} {item['city']} hotel"
        for attempt in range(3):
            try:
                results = list(d.images(query, max_results=1))
                if results:
                    item['image'] = results[0]['image']
                    print(f"✓ [{item['id']:3d}] {item['name'][:50]}")
                else:
                    print(f"✗ [{item['id']:3d}] {item['name'][:50]} (no results)")
                break
            except Exception as e:
                print(f"  [{item['id']:3d}] attempt {attempt+1} failed: {e}")
                time.sleep(5)

json.dump(raw, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("\nDone. Run: python manage.py sync_hotels")
