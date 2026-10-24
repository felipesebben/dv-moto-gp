"""Shared geometry + drawing helpers for the layout sketches (scratch tool)."""

import csv
import json
import math
from pathlib import Path

C = {
    "bg": "#1C1A19",
    "ink": "#F2EFE9",
    "muted": "#A8A29A",
    "rule": "#3A3734",
    "card": "#252220",
    "rossi": "#FDF504",
    "capi": "#F26B5B",
    "grey": "#6F6A64",
    "green": "#229457",
}
POS = {
    46: [3, 1, 2, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 4, 3, 2, 2, 2, 2, 2, 1],
    65: [2, 8, 8, 8, 8, 7, 7, 7, 7, 5, 5, 4, 4, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    69: [4, 7, 6, 5, 6, 6, 6, 6, 5, 4, 3, 3, 3, 4, 4, 3, 2, 2, 3, 3, 3, 3, 3, 3],
    15: [1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 6, 5, 5, 5, 5, 5, 5],
    33: [6, 3, 3, 3, 2, 4, 4, 3, 4, 3, 4, 5, 5, 5, 5, 4, 3, 4, 6, 6, 6, 6, 6, 6],
    26: [8, 6, 7, 7, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 4, 4, 4, 4, 4, 4],
}
CONTEXT = (69, 15, 33, 26)
ROSSI_MOMENTS = {1, 4, 5, 6, 7}
RIVAL_MOMENTS = {2, 3}  # Capirossi's charge: coral ring


def load(
    root: Path,
) -> tuple[list[tuple[float, float]], dict[int, tuple[str, int]], list[dict[str, str]]]:
    """Track rotated to TV orientation (north left), unit box ~1000 wide; corners; moments."""
    coords = json.loads((root / "seeds" / "mugello.geojson").read_text(encoding="utf-8"))[
        "features"
    ][0]["geometry"]["coordinates"]
    k = math.cos(math.radians(coords[0][1]))
    xs = [p[0] * k for p in coords]
    ys = [-p[1] for p in coords]
    s = 1000 / max(max(xs) - min(xs), max(ys) - min(ys))
    north_up = [((x - min(xs)) * s, (y - min(ys)) * s) for x, y in zip(xs, ys, strict=True)]
    tw = max(p[0] for p in north_up)
    track = [(y, tw - x) for x, y in north_up]
    corners = {
        int(r["turn"]): (r["corner_name"], int(r["point_idx"]))
        for r in csv.DictReader((root / "seeds" / "corners.csv").open(encoding="utf-8"))
    }
    moments = list(csv.DictReader((root / "seeds" / "key_moments.csv").open(encoding="utf-8")))
    return track, corners, moments


def fit(track: list[tuple[float, float]], x: float, y: float, w: float, h: float):
    tw = max(p[0] for p in track)
    th = max(p[1] for p in track)
    sc = min(w / tw, h / th)
    ox, oy = x + (w - tw * sc) / 2, y + (h - th * sc) / 2
    return [(ox + px * sc, oy + py * sc) for px, py in track]


def path(pts: list[tuple[float, float]], close: bool = False) -> str:
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return d + (" Z" if close else "")


def resample(pts: list[tuple[float, float]], n: int) -> list[tuple[float, float]]:
    """Uniform arc-length resampling of a closed polyline (first point = start line)."""
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg)
    out, i, acc = [], 0, 0.0
    for j in range(n):
        target = total * j / n
        while acc + seg[i] < target:
            acc += seg[i]
            i += 1
        t = (target - acc) / seg[i]
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
    return out


def smooth(pts: list[tuple[float, float]], window: int, passes: int) -> list[tuple[float, float]]:
    n = len(pts)
    for _ in range(passes):
        pts = [
            (
                sum(pts[(i + k) % n][0] for k in range(-window, window + 1)) / (2 * window + 1),
                sum(pts[(i + k) % n][1] for k in range(-window, window + 1)) / (2 * window + 1),
            )
            for i in range(n)
        ]
    return pts


def outward_normals(pts: list[tuple[float, float]]) -> list[tuple[float, float]]:
    n = len(pts)
    cx = sum(p[0] for p in pts) / n
    cy = sum(p[1] for p in pts) / n
    normals = []
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i - 1], pts[(i + 1) % n]
        tx, ty = x1 - x0, y1 - y0
        L = math.hypot(tx, ty) or 1
        normals.append((ty / L, -tx / L))
    sign = (
        1
        if sum(
            nx * (p[0] - cx) + ny * (p[1] - cy) for (nx, ny), p in zip(normals, pts, strict=True)
        )
        > 0
        else -1
    )
    return [(nx * sign, ny * sign) for nx, ny in normals]


def smoothstep(t: float) -> float:
    return t * t * (3 - 2 * t)


def position_at(series: list[int], lap_f: float) -> float:
    lo = min(int(lap_f), 22)
    t = smoothstep(lap_f - lo)
    return series[lo] + (series[lo + 1] - series[lo]) * t


def badge(x: float, y: float, n: int, r: float = 13) -> str:
    rossi = n in ROSSI_MOMENTS
    fill = C["rossi"] if rossi else C["bg"]
    stroke = C["bg"] if rossi else C["capi"] if n in RIVAL_MOMENTS else C["ink"]
    ink = C["bg"] if rossi else C["ink"]
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        f'<text x="{x:.1f}" y="{y + r * 0.38:.1f}" class="badge" font-size="{r * 1.05:.0f}" '
        f'fill="{ink}">{n}</text>'
    )


def ordinal(n: int) -> str:
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n, 'th') }"


def signed_area(pts: list[tuple[float, float]]) -> float:
    return sum(pts[i - 1][0] * pts[i][1] - pts[i][0] * pts[i - 1][1] for i in range(len(pts))) / 2


def envelope(
    track_pts: list[tuple[float, float]], n: int, window: int
) -> list[tuple[float, float]]:
    """Rounded convex envelope of the track, same direction as racing, starting nearest the line."""
    pts = sorted(set(track_pts))

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    if (signed_area(hull) > 0) != (signed_area(track_pts) > 0):
        hull.reverse()
    ring = resample(hull + [hull[0]], n)
    ring = smooth(ring, window, 2)
    start = min(range(n), key=lambda i: math.dist(ring[i], track_pts[0]))
    return ring[start:] + ring[:start]
