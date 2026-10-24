"""Circuit outline (GeoJSON LineString) -> ordered points with distance along the lap."""

import json
import math
from pathlib import Path

import polars as pl

EARTH_RADIUS_M = 6_371_008.8


def haversine_m(a: tuple[float, float], b: tuple[float, float]) -> float:
    """Distance in metres between two (lon, lat) points."""
    lat1, lat2 = math.radians(a[1]), math.radians(b[1])
    dlat, dlon = lat2 - lat1, math.radians(b[0] - a[0])
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(h))


def parse_track(path: Path) -> pl.DataFrame:
    coords = json.loads(path.read_text(encoding="utf-8"))["features"][0]["geometry"]["coordinates"]
    distance, rows = 0.0, []
    for idx, (lon, lat) in enumerate(coords):
        if idx:
            distance += haversine_m(tuple(coords[idx - 1]), (lon, lat))
        rows.append({"point_idx": idx, "lon": lon, "lat": lat, "distance_m": distance})
    return pl.DataFrame(rows)
