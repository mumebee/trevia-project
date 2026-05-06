import json, time, random
from ddgs import DDGS

JSON_PATH = 'static/data/restaurants.json'
data = json.load(open(JSON_PATH, encoding='utf-8'))

updated = 0
failed = 0

with DDGS() as d:
    for i, item in enumerate(data):
        if item['country'] == 'Uzbekistan':
            continue
        query = f"{item['name']} {item['city']} restaurant"
        try:
            results = list(d.images(query, max_results=1))
            if results:
                item['image'] = results[0]['image']
                updated += 1
                print(f"✓ [{i:3d}] {item['name'][:40]} ({item['city']})")
            else:
                failed += 1
                print(f"✗ [{i:3d}] {item['name'][:40]} (no results)")
        except Exception as e:
            failed += 1
            print(f"✗ [{i:3d}] {item['name'][:40]} ({e})")
        time.sleep(random.uniform(0.8, 1.5))

json.dump(data, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nDone. Updated: {updated}, Failed: {failed}")
print("Run: python manage.py sync_rest")
