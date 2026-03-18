"""
Downloads the Israel Post branches JSON and builds:
  1. docs/cities/<city_name>.json  — one file per city, ALL fields preserved
  2. docs/cities_list.json         — lightweight list of all cities + branch count + file URL

This way Claude fetches only the one city it needs (~500–25,000 tokens depending on city size),
with zero data loss compared to the original file.
"""

import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://mypostvouchars-prd.azureedge.net/branches/branches.json"
CITIES_DIR = Path("docs/cities")
LIST_PATH  = Path("docs/cities_list.json")

def fetch_branches():
    print(f"Downloading from {SOURCE_URL}...")
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as r:
        data = json.load(r)
    branches = data["Result"]
    print(f"  {len(branches)} branches loaded")
    return branches

def build_city_files(branches):
    CITIES_DIR.mkdir(parents=True, exist_ok=True)

    # Group by city
    by_city = {}
    for b in branches:
        city = (b.get("city") or "").strip()
        if not city:
            continue
        by_city.setdefault(city, []).append(b)

    # Write one file per city — full data, nothing removed
    for city, city_branches in by_city.items():
        path = CITIES_DIR / f"{city}.json"
        path.write_text(
            json.dumps(city_branches, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8"
        )

    return by_city

def build_cities_list(by_city, updated):
    """Lightweight index: city name → branch count + filename.
    Claude fetches this first (~1,000 tokens) to find the right city file,
    then fetches only that city's file.
    """
    cities_list = {
        "updated": updated,
        "cities": {
            city: {
                "count": len(branches),
                "file": f"cities/{city}.json"
            }
            for city, branches in sorted(by_city.items())
        }
    }
    LIST_PATH.write_text(
        json.dumps(cities_list, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )
    return cities_list

def main():
    updated = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    branches = fetch_branches()
    by_city  = build_city_files(branches)
    cities_list = build_cities_list(by_city, updated)

    print(f"\n  {len(by_city)} city files written to {CITIES_DIR}/")
    print(f"  cities_list.json written to {LIST_PATH}")

    # Print size stats
    total_kb = sum((CITIES_DIR / f"{c}.json").stat().st_size for c in by_city) / 1024
    list_kb  = LIST_PATH.stat().st_size / 1024
    print(f"\n  cities_list.json size: {list_kb:.1f} KB")
    print(f"  Total city files size: {total_kb:.1f} KB")

    # Show biggest cities
    print("\n  Largest city files:")
    sizes = sorted(
        [(c, (CITIES_DIR / f"{c}.json").stat().st_size) for c in by_city],
        key=lambda x: -x[1]
    )[:10]
    for city, size in sizes:
        print(f"    {city}: {size/1024:.1f} KB (~{size//4} tokens)")

if __name__ == "__main__":
    main()
