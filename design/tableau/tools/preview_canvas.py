"""Preview what the Tableau canvas sheets should look like, read straight from the .hyper.

Run: uv run python design/tableau/tools/preview_canvas.py
Writes design/tableau/previews/{map,race}_canvas.html; screenshot them to PNG with a headless
browser at the sheet size. The geometry is projected with Web Mercator, as Tableau does, and
fitted to the frame, so the previews show exactly what the sheets should draw.
"""

import math
import re
import tempfile
from pathlib import Path

from tableauhyperapi import Connection, HyperProcess, Telemetry

ROOT = Path(__file__).resolve().parents[3]
HYPER = ROOT / "data" / "processed" / "mugello06.hyper"
OUT = ROOT / "design" / "tableau" / "previews"
SHEETS = {"map_features": ("map_canvas", 1328, 992), "race_features": ("race_canvas", 1728, 560)}
C = {"bg": "#1C1A19", "ink": "#F2EFE9", "muted": "#A8A29A", "protagonist": "#FDF504",
     "rival": "#F26B5B", "other": "#6F6A64", "green": "#229457"}
# (layer, role filter or None, colour, width), drawn bottom to top, as in docs/TABLEAU_GUIDE.md
LINES = [
    ("track", None, C["ink"], 7), ("stretch", None, C["protagonist"], 9),
    ("start_line", None, C["green"], 6), ("leader", None, C["muted"], 1),
    ("axis", None, C["muted"], 1), ("tick", None, C["muted"], 1), ("connector", "role", None, 1.5),
    ("line", "other", C["other"], 1.5), ("line", "rival", C["rival"], 3),
    ("halo", None, C["bg"], 7), ("line", "protagonist", C["protagonist"], 4),
    ("key_line", None, C["protagonist"], 6),
]
TEXT = {"corner_label": (14, C["muted"], 500), "callout": (17, C["ink"], 600),
        "axis_label": (14, C["muted"], 500), "end_label": (15, C["ink"], 600),
        "key_label": (14, C["muted"], 400)}
ANCHOR = {"right": "start", "left": "end", "center": "middle"}


def projected(wkt: str) -> list[tuple[float, float]]:
    pairs = re.findall(r"(-?[\d.]+) (-?[\d.]+)", wkt)
    return [(math.radians(float(lon)), math.log(math.tan(math.pi / 4 + math.radians(float(lat)) / 2)))
            for lon, lat in pairs]


def draw(rows: list[tuple[str, str | None, str | None, str | None, str]], w: int, h: int) -> str:
    frame = [projected(g)[0] for layer, *_, g in rows if layer == "frame"]
    x0, x1 = min(p[0] for p in frame), max(p[0] for p in frame)
    y1 = max(p[1] for p in frame)
    s = w / (x1 - x0)

    def pts(g: str) -> list[tuple[float, float]]:
        return [((x - x0) * s, (y1 - y) * s) for x, y in projected(g)]

    svg = [f'<rect width="{w}" height="{h}" fill="{C["bg"]}"/>']
    for name, role, colour, width in LINES:
        for layer, _, r, _, g in rows:
            if layer == name and (role in (None, "role") or r == role):
                stroke = colour or C[r or "other"]
                line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts(g))
                svg.append(f'<polyline points="{line}" fill="none" stroke="{stroke}" '
                           f'stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    for layer, _, r, label, g in rows:
        (x, y), = pts(g) if layer in ("corner_dot", "rider_dot", "badge") else [(0, 0)]
        if layer == "corner_dot":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["muted"]}"/>')
        elif layer == "rider_dot":
            svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{C[r or "other"]}" '
                       f'stroke="{C["bg"]}" stroke-width="2"/>')
        elif layer == "badge":
            rossi = r == "protagonist"
            svg.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="12" fill="{C["protagonist"] if rossi else C["bg"]}" '
                f'stroke="{C["bg"] if rossi else C["rival"]}" stroke-width="2"/>'
                f'<text x="{x:.1f}" y="{y + 4.5:.1f}" font-family="Barlow Condensed" font-weight="700" '
                f'font-size="13" text-anchor="middle" fill="{C["bg"] if rossi else C["ink"]}">{label}</text>')
    for layer, align, _, label, g in rows:
        if layer in TEXT:
            size, colour, weight = TEXT[layer]
            ((x, y),) = pts(g)
            svg.append(f'<text x="{x:.1f}" y="{y + size * 0.35:.1f}" font-family="Barlow Condensed" '
                       f'font-weight="{weight}" font-size="{size}" fill="{colour}" '
                       f'text-anchor="{ANCHOR[align or "center"]}">{label}</text>')
    return (f'<html><head><link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
            f'family=Barlow+Condensed:wght@400;500;600;700&amp;display=swap"></head>'
            f'<body style="margin:0"><svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}">'
            + "".join(svg) + "</svg></body></html>")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp, \
            HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters={"log_dir": tmp}) as hyper, \
            Connection(hyper.endpoint, HYPER) as con:
        for table, (name, w, h) in SHEETS.items():
            rows = con.execute_list_query(
                f'SELECT layer, align, role, label, wkt FROM "{table}"')
            (OUT / f"{name}.html").write_text(draw(rows, w, h), encoding="utf-8")
            print(f"wrote {OUT / name}.html ({w} x {h})")
