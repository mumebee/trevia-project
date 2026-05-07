import json, time
from ddgs import DDGS

JSON_PATH = 'static/data/restaurants.json'
data = json.load(open(JSON_PATH, encoding='utf-8'))

MISSED_IDX = {50, 51, 57, 60, 65, 67, 76, 82, 89, 90, 99, 102, 103, 110, 111, 113, 116, 117, 124, 125, 127, 129, 142, 150, 151, 157, 159, 170, 173, 178, 182, 184, 186, 191, 192, 198, 199, 203}

with DDGS() as d:
    for i, item in enumerate(data):
        if i not in MISSED_IDX:
            continue
        query = f"{item['name']} {item['city']} restaurant"
        for attempt in range(3):
            try:
                results = list(d.images(query, max_results=1))
                if results:
                    item['image'] = results[0]['image']
                    print(f"✓ [{i:3d}] {item['name'][:50]} ({item['city']})")
                else:
                    print(f"✗ [{i:3d}] {item['name'][:50]} (no results)")
                break
            except Exception as e:
                print(f"  [{i:3d}] attempt {attempt+1} failed: {e}")
                time.sleep(5)

json.dump(data, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print("\nDone. Run: python manage.py sync_rest")
