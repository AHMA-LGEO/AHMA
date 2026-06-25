"""
One-time preprocessing: convert subregion shapefiles to fast-loading cache files.

Run this once before starting the app:
    python preprocess_subregion_cache.py

Creates two files per CD in source/mapdata_simplified/subregion_cache/:
  {code}.geojson      - pre-simplified geometry for Plotly (~50-200ms to load)
  {code}_attrs.csv    - CSDNAME/lat/lon attributes (~5-10ms to load)

Together these replace the 3-5s shapefile pipeline with ~100-200ms cold loads.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import geopandas as gpd
from dashboard_helpers.config import SUBREGION_DATA_DIR, SUBREGION_CACHE_DIR

SIMPLIFY_TOLERANCE = 0.001


def preprocess():
    SUBREGION_CACHE_DIR.mkdir(exist_ok=True)
    shp_files = sorted(SUBREGION_DATA_DIR.glob("*.shp"))

    if not shp_files:
        print(f"No .shp files found in {SUBREGION_DATA_DIR}")
        return

    print(f"Found {len(shp_files)} shapefiles -> writing cache to {SUBREGION_CACHE_DIR}\n")

    for i, shp_file in enumerate(shp_files, 1):
        region_code = shp_file.stem
        geojson_path = SUBREGION_CACHE_DIR / f"{region_code}.geojson"
        attrs_path = SUBREGION_CACHE_DIR / f"{region_code}_attrs.csv"

        if geojson_path.exists() and attrs_path.exists():
            print(f"[{i:2}/{len(shp_files)}] {region_code}: already cached, skipping")
            continue

        print(f"[{i:2}/{len(shp_files)}] {region_code}: reading...", end=" ", flush=True)
        gdf = gpd.read_file(shp_file)
        gdf = gdf.set_index("CSDUID")

        print("simplifying...", end=" ", flush=True)
        gdf.geometry = gdf.geometry.simplify(SIMPLIFY_TOLERANCE, preserve_topology=True)

        print("saving...", end=" ", flush=True)
        geojson = json.loads(gdf.geometry.to_json())
        with open(geojson_path, "w") as f:
            json.dump(geojson, f, separators=(",", ":"))

        gdf[["CSDNAME", "lat", "lon"]].to_csv(attrs_path)
        print("done")

    print(f"\nCache complete. Restart the app to use it.")


if __name__ == "__main__":
    preprocess()
