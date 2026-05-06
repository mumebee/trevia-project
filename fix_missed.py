import json, time
from ddgs import DDGS

JSON_PATH = 'static/data/activities.json'
data = json.load(open(JSON_PATH, encoding='utf-8'))

MISSED_IDS = {367, 368, 369}

with DDGS() as d:
    for item in data:
        if item['id'] not in MISSED_IDS:
            continue
        query = f"{item['name']} {item['city']}"
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
                print(f"  attempt {attempt+1} failed: {e}")
                time.sleep(5)

json.dump(data, open(JSON_PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=4)
print("\nDone.")
