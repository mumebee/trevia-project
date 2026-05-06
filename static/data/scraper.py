"""
scraper.py — Google Images via Custom Search JSON API (free, no captcha)

Setup (5 min):
  1. Go to https://developers.google.com/custom-search/v1/introduction
     → "Get a Key" → create a project → copy API key

  2. Go to https://programmablesearchengine.google.com/
     → "Add" → set name → under "Search the entire web" toggle ON
     → Copy the "Search engine ID" (cx)

  3. pip install requests
     python scraper.py --key YOUR_API_KEY --cx YOUR_CX_ID

Free tier: 100 queries/day
370 items → 4 days, or create 4 free Google accounts and run in parallel.
"""

import json
import time
import argparse
import random
from pathlib import Path
import requests

GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"


def get_first_image(query: str, api_key: str, cx: str) -> str | None:
    params = {
        "key":        api_key,
        "cx":         cx,
        "q":          query,
        "searchType": "image",
        "num":        1,        # we only need 1 result
        "safe":       "active",
    }
    try:
        resp = requests.get(GOOGLE_CSE_URL, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items", [])
        if items:
            return items[0].get("link")  # direct image URL
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 429:
            print("   ⏳ Rate limited — waiting 60s...")
            time.sleep(60)
        elif resp.status_code == 403:
            print("   ❌ Quota exceeded for today (100/day limit hit)")
            return "QUOTA_EXCEEDED"
        else:
            print(f"   ❌ HTTP {resp.status_code}: {e}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default="activities.json")
    parser.add_argument("--output", default="activities_new.json")
    parser.add_argument("--key",    required=True, help="Google API key")
    parser.add_argument("--cx",     required=True, help="Custom Search Engine ID")
    parser.add_argument("--resume", action="store_true",
                        help="Skip items that already have a non-placeholder image")
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))

    # Load existing output if resuming
    out_path = Path(args.output)
    existing = {}
    if args.resume and out_path.exists():
        for item in json.loads(out_path.read_text(encoding="utf-8")):
            existing[item["id"]] = item
        print(f"▶  Resuming — {len(existing)} items already processed\n")

    results = []
    updated = 0
    quota_hit = False

    for i, activity in enumerate(data, 1):
        aid = activity["id"]

        # Resume: skip if already has a real image from a previous run
        if args.resume and aid in existing:
            cached = existing[aid]
            if cached.get("image") and "unsplash" not in cached["image"] and \
               "placeholder" not in cached["image"]:
                results.append(cached)
                print(f"[{i:>4}/{len(data)}] ⏭  [{aid}] {activity['name'][:40]} — skipped (cached)")
                continue

        if quota_hit:
            # Drain remaining items with original images
            results.append(activity)
            continue

        query = f"{activity['name']} {activity.get('city', '')} {activity.get('country', '')}"
        print(f"[{i:>4}/{len(data)}] 🔍 [{aid}] {query[:55]}")

        img_url = get_first_image(query, args.key, args.cx)

        if img_url == "QUOTA_EXCEEDED":
            quota_hit = True
            results.append(activity)
            print(f"   ⚠  Quota hit at item {i}/{len(data)} — saving progress and stopping")
            # Save what we have so far so --resume works next run
            _save(results + data[i:], out_path)
            print(f"\n💾 Partial save → {args.output}")
            print(f"   Run again tomorrow with --resume to continue from item {i+1}")
            return
        elif img_url:
            print(f"   ✅ {img_url[:85]}")
            results.append({**activity, "image": img_url})
            updated += 1
        else:
            print(f"   ⚠  No result — keeping original")
            results.append(activity)

        # Small delay to stay under burst limits (not strictly needed but polite)
        time.sleep(random.uniform(0.3, 0.7))

    _save(results, out_path)
    print(f"\n✅ Done! {updated}/{len(data)} images updated → {args.output}")


def _save(results, path):
    tmp = path.with_suffix(".tmp.json")
    tmp.write_text(json.dumps(results, ensure_ascii=False, indent=4), encoding="utf-8")
    tmp.replace(path)


if __name__ == "__main__":
    main()