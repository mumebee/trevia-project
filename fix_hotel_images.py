import json, time, random
from ddgs import DDGS

JSON_PATH = 'static/data/hotels.json'
raw = json.load(open(JSON_PATH, encoding='utf-8'))
data = raw['hotels']

updated = 0
failed = 0

with DDGS() as d:
    for item in data:
        query = f"{item['name']} {item['city']} hotel"
        try:
            results = list(d.images(query, max_results=1))
            if results:
                item['image'] = results[0]['image']
                updated += 1
                print(f"✓ [{item['id']:3d}] {item['name'][:40]}")
            else:
                failed += 1
                print(f"✗ [{item['id']:3d}] {item['name'][:40]} (no results)")
        except Exception as e:
            failed += 1
            print(f"✗ [{item['id']:3d}] {item['name'][:40]} ({e})")
        time.sleep(random.uniform(0.8, 1.5))

json.dump(raw, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f"\nDone. Updated: {updated}, Failed: {failed}")
