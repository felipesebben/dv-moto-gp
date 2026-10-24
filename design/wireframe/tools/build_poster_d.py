"""Refined wireframe for layout D (140 x 85 cm landscape).

Run: uv run python design/wireframe/tools/build_poster_d.py
Writes design/wireframe/poster_d.html. Sketch tool only: the real poster is built in Tableau.
Event facts below are copied from the official classification PDF and the track GeoJSON;
the build will read them from the pipeline instead.
"""

import base64
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sketchlib import (  # noqa: E402
    C, CONTEXT, POS, ROSSI_MOMENTS, badge, fit, load, ordinal, path, position_at,
)

ROOT = Path(__file__).resolve().parents[3]
# --with-images embeds the user's local helmet + 46 logo (third-party images) into a
# git-ignored preview; the committed wireframe keeps placeholders
WITH_IMAGES = "--with-images" in sys.argv
IMAGES = ROOT / "data" / "interim" / "images"  # made by prepare_images.py
OUT = ROOT / "design" / "wireframe" / ("poster_d_preview.html" if WITH_IMAGES else "poster_d.html")
track, corners, moments = load(ROOT)

PX = 1.6  # px per mm
W, H = round(1400 * PX), round(850 * PX)
M = 104  # 65 mm margin
COL = 1640  # story column
RIGHT = W - M
ITALY = {"green": "#229457", "white": C["ink"], "red": "#CE2B37"}  # flag red, kept apart from Capirossi's coral

# ---- map placement ------------------------------------------------------------
CONTENT_TOP = 430  # shared top edge: circuit band, map, key numbers, story column
MAP = (440, CONTENT_TOP + 12, 800, 540)  # x, y, w, h (height-bound); corner labels sit above
pts = fit(track, *MAP)
SCALE = MAP[3] / 705
CALLOUT = {0: (-136, -204, -20, 5, "end"), 1: (-14, 141, -12, 32, "start"),
           8: (-8, -125, -12, 32, "start"), 9: (-54, 35, -20, 5, "end")}
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end")}
STRETCHES = [range(7, 14), range(57, 65), [*range(125, 129), 0]]

svg: list[str] = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']

# ---- header: MUGELLO 2006 (+ Italian livery flash) above the title, then one paragraph ----
KICKER_Y, TITLE_Y = 118, 244
svg.append(f'<text id="kicker" x="{M}" y="{KICKER_Y}" class="kicker">MUGELLO 2006</text>')
# drawn at x=0; the page script moves it to the measured end of the kicker
svg.append('<g class="flash" data-for="kicker">' + "".join(
    f'<polygon points="{i * 10 + 12},{KICKER_Y - 24} {i * 10 + 18},{KICKER_Y - 24} '
    f'{i * 10 + 6},{KICKER_Y} {i * 10},{KICKER_Y}" fill="{c}"/>'
    for i, c in enumerate(ITALY.values())
) + "</g>")
svg.append(f'<text x="{M - 6}" y="{TITLE_Y}" class="title">THE ROSSI COMEBACK</text>')
# one paragraph: the event and date run in, then what happened and why it matters
svg.append(
    f'<foreignObject x="{M}" y="270" width="1380" height="110"><div xmlns="http://www.w3.org/1999/xhtml" class="standfirst">'
    f"<span class=\"runin\">Gran Premio d&#8217;Italia Alice, 4 June 2006.</span> "
    f"Forty-three points down in the championship and in front of his home crowd, Valentino Rossi "
    f"was leading when he ran wide at San Donato and fell to fifth, with eight laps left. He hunted "
    f"Loris Capirossi down lap after lap and, on the final lap, passed him for the win at the same "
    f"corner. Patience, then one perfect move: a race still counted among his greatest."
    f"</div></foreignObject>"
)

# ---- image: the 46 logo, top-right ------------------------------
def picture(name: str, label: str, x: float, y: float, w: float, h: float) -> str:
    """The real image in a local preview (--with-images), otherwise a placeholder box."""
    src = IMAGES / f"{name}.png"
    if WITH_IMAGES and src.exists():
        data = base64.b64encode(src.read_bytes()).decode()
        return (f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMaxYMid meet" '
                f'href="data:image/png;base64,{data}"/>')
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="none" stroke="{C["muted"]}" '
            f'stroke-dasharray="4 4"/><text x="{x + w / 2}" y="{y + h / 2 + 6}" class="ph">IMAGE · {label}</text>')


# only the 46 logo (no helmet: keep the attention on the map and charts), right-aligned
svg.append(picture("logo46", "46 logo", RIGHT - 300, TITLE_Y - 136, 300, 136))

# ---- map ----------------------------------------------------------------------
svg.append(f'<path d="{path(pts, True)}" fill="none" stroke="{C["ink"]}" stroke-width="7" stroke-linejoin="round"/>')
for s in STRETCHES:
    svg.append(f'<path d="{path([pts[i] for i in s])}" fill="none" stroke="{C["rossi"]}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>')
cx = sum(p[0] for p in pts) / len(pts)
cy = sum(p[1] for p in pts) / len(pts)
sx, sy = pts[0]
svg.append(f'<rect x="{sx - 3:.1f}" y="{sy - 14:.1f}" width="6" height="28" fill="{C["green"]}"/>')
svg.append(f'<text x="{sx + 10:.1f}" y="{sy - 12:.1f}" class="corner">Start / Finish</text>')
for turn, (name, idx) in corners.items():
    if turn == 0:
        continue
    x, y = pts[idx]
    vx, vy = x - cx, y - cy
    n = math.hypot(vx, vy) or 1
    lx, ly, anchor = x + vx / n * 16, y + vy / n * 16 + 4, "start" if vx > 0 else "end"
    if turn in LABEL_FIX:
        dx, dy, anchor = LABEL_FIX[turn]
        lx, ly = x + dx, y + dy
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["muted"]}"/>')
    svg.append(f'<text x="{lx:.1f}" y="{ly:.1f}" class="corner" text-anchor="{anchor}">{name}</text>')
by_turn: dict[int, list[dict[str, str]]] = {}
for m in moments:
    if m["turn"]:
        by_turn.setdefault(int(m["turn"]), []).append(m)
for turn, ms in by_turn.items():
    x, y = pts[corners[turn][1]]
    ux, uy, tdx, tdy, anchor = CALLOUT[turn]
    bx, by = x + ux * SCALE, y + uy * SCALE
    for j, m in enumerate(ms):
        svg.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx + j * 30:.1f}" y2="{by:.1f}" stroke="{C["muted"]}" stroke-width="1"/>')
        svg.append(badge(bx + j * 30, by, int(m["moment_id"])))
    for j, m in enumerate(ms):
        svg.append(f'<text x="{bx + tdx:.1f}" y="{by + tdy + j * 18:.1f}" class="callout" text-anchor="{anchor}">{m["moment_id"]} · {m["headline"]}</text>')

# circuit block, left band: where Mugello is in Italy, then the facts
# (circuit information + classification PDFs; name and town from the track GeoJSON;
# Italy outline from Natural Earth, public domain)
svg.append(f'<text x="{M}" y="{CONTENT_TOP + 11}" class="eyebrow">THE CIRCUIT</text>')
italy = json.loads((ROOT / "seeds" / "italy.geojson").read_text(encoding="utf-8"))
kx = math.cos(math.radians(42))
rings = [[(lon * kx, -lat) for lon, lat in poly[0]] for poly in italy["features"][0]["geometry"]["coordinates"]]
allx = [x for r in rings for x, _ in r]
ally = [y for r in rings for _, y in r]
box_x, box_y, box_w, box_h = M, CONTENT_TOP + 28, 250, 250
isc = min(box_w / (max(allx) - min(allx)), box_h / (max(ally) - min(ally)))


def ip(x: float, y: float) -> tuple[float, float]:
    return box_x + (x - min(allx)) * isc, box_y + (y - min(ally)) * isc


for r in rings:
    svg.append(f'<path d="{path([ip(x, y) for x, y in r], True)}" fill="#2A2725" stroke="{C["muted"]}" stroke-width="1" stroke-linejoin="round"/>')
mx, my = ip(11.372 * kx, -43.997)  # Mugello
svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="9" fill="none" stroke="{C["rossi"]}" stroke-width="2"/>')
svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3.5" fill="{C["rossi"]}"/>')
svg.append(f'<text x="{mx + 16:.1f}" y="{my + 5:.1f}" class="placename">Mugello</text>')
card_x, card_y = M, CONTENT_TOP + 300
svg.append(f'<text x="{card_x}" y="{card_y + 24}" class="circuit">Autodromo Internazionale del Mugello</text>')
for i, line in enumerate([
    "Scarperia e San Piero, Tuscany · built 1974",
    "5,245 m long · 14 m wide · clockwise",
    "15 corners: 9 right, 6 left",
    "Longest straight 1,141 m",
    "Race: 23 laps · 120.6 km · dry, air 20 °C, track 29 °C",
]):
    svg.append(f'<text x="{card_x}" y="{card_y + 50 + i * 23}" class="meta">{line}</text>')

# key numbers, right of the circuit, each tied to its moment
STATS = [  # in race order (badges 4, 6, 7); values from poster.timeline
    ("0.730 s", "behind Capirossi after running wide, in 5th", 4),
    ("0.002 s", "between them after lap 22", 6),
    ("0.575 s", "Rossi&#8217;s winning margin", 7),
]
for i, (v, label, n) in enumerate(STATS):
    y = CONTENT_TOP + 34 + i * 96  # first figure's cap height starts on the grid line
    svg.append(f'<text x="1300" y="{y}" class="stat">{v}</text>')
    svg.append(f'<text x="1302" y="{y + 22}" class="statlabel">{label}</text>')
    if n:
        svg.append(badge(1282, y - 16, n, r=9))

# ---- story column ---------------------------------------------------------------
top, slot = CONTENT_TOP - 4, 119
svg.append(f'<line x1="{COL + 12}" y1="{top + 28}" x2="{COL + 12}" y2="{top + 6 * slot + 28}" stroke="{C["rule"]}" stroke-width="2"/>')
for i, m in enumerate(moments):
    y = top + i * slot
    n = int(m["moment_id"])
    svg.append(badge(COL + 12, y + 28, n, r=12))
    svg.append(f'<rect x="{COL + 38}" y="{y + 6}" width="3" height="{slot - 24}" fill="{C["rossi"] if n in ROSSI_MOMENTS else C["grey"]}"/>')
    svg.append(
        f'<foreignObject x="{COL + 52}" y="{y + 4}" width="{RIGHT - COL - 52}" height="{slot - 8}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="vcard"><b><i>LAP {m["lap"]}</i> {m["headline"]}</b>'
        f'<span>{m["story"]}</span></div></foreignObject>'
    )

# ---- position strip ---------------------------------------------------------------
x0, x1, axis_y, row = M + 64, 1500, 1080, 16


def lx(lap: float) -> float:
    return x0 + lap * (x1 - x0) / 23


def ry(pos: float) -> float:
    return axis_y + 22 + (pos - 1) * row


svg.append(f'<text x="{M}" y="{axis_y - 26}" class="eyebrow">POSITIONS, LAP BY LAP <tspan class="hint">· higher = further ahead</tspan></text>')
svg.append(f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{C["muted"]}"/>')
for p_ in (1, 4, 8):
    svg.append(f'<text x="{x0 - 14}" y="{ry(p_) + 4:.1f}" class="axis" text-anchor="end">{ordinal(p_)}</text>')
for lap in (0, 5, 10, 15, 20, 23):
    svg.append(f'<text x="{lx(lap):.1f}" y="{ry(8) + 28:.1f}" class="axis">{"Grid" if lap == 0 else f"Lap {lap}"}</text>')
for m in moments:
    svg.append(f'<line x1="{lx(int(m["lap"])):.1f}" y1="{axis_y + 10}" x2="{lx(int(m["lap"])):.1f}" y2="{ry(8) + 8:.1f}" stroke="{C["rule"]}"/>')


def hline(r: int) -> str:
    return " ".join(f"{lx(t / 10):.1f},{ry(position_at(POS[r], t / 10)):.1f}" for t in range(231))


for r in CONTEXT:
    svg.append(f'<polyline points="{hline(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>')
svg.append(f'<polyline points="{hline(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>')
for m in moments:
    svg.append(badge(lx(int(m["lap"])), axis_y, int(m["moment_id"]), r=10))
for r, label in ((46, "Rossi · 1st"), (65, "Capirossi · 2nd")):
    y = ry(POS[r][-1])
    svg.append(f'<circle cx="{lx(23):.1f}" cy="{y:.1f}" r="5" fill="{C["rossi"] if r == 46 else C["capi"]}" stroke="{C["bg"]}" stroke-width="2"/>')
    svg.append(f'<text x="{lx(23) + 12:.1f}" y="{y + 4:.1f}" class="endlabel">{label}</text>')

# ---- footer: discreet map key (left) + credits (right) ---------------------------
fy = H - 48
svg.append(badge(M + 9, fy - 5, 4, r=10))
svg.append(f'<text x="{M + 26}" y="{fy}" class="foot">Rossi moment</text>')
svg.append(badge(M + 170, fy - 5, 2, r=10))
svg.append(f'<text x="{M + 188}" y="{fy}" class="foot">other moment</text>')
svg.append(f'<line x1="{M + 340}" y1="{fy - 5}" x2="{M + 362}" y2="{fy - 5}" stroke="{C["rossi"]}" stroke-width="6" stroke-linecap="round"/>')
svg.append(f'<text x="{M + 374}" y="{fy}" class="foot">where it happened</text>')
svg.append(f'<text x="{M + 560}" y="{fy}" class="foot">Numbers match the stories on the right.</text>')
QR_S = 64  # 40 mm in print: still easy to scan
qr = (ROOT / "design" / "wireframe" / "assets" / "qr_full_race.svg").read_text(encoding="utf-8")
qr = qr.replace('<svg xmlns="http://www.w3.org/2000/svg" width="37" height="37"',
                f'<svg x="{RIGHT - QR_S}" y="{fy - QR_S + 6}" width="{QR_S}" height="{QR_S}" viewBox="0 0 37 37"', 1)
svg.append(qr)
svg.append(f'<text x="{RIGHT - QR_S - 14}" y="{fy - 30}" class="foot" text-anchor="end">Watch the race</text>')
svg.append(
    f'<text x="{RIGHT - QR_S - 14}" y="{fy}" class="foot" text-anchor="end">Data: official MotoGP timing (Tissot / Dorna) · '
    f"Track: bacinger/f1-circuits (MIT) · Story: MotoGP broadcast, Paddock Pass Podcast</text>"
)


# ---- type scale (px at 1.6 px/mm; 1 px = 1.77 pt in print). Nothing below MIN_PT. ----
PT_PER_PX = 72 / 25.4 / PX
MIN_PT = 24  # our floor for anything on the poster (the hard rule is 10 pt)
TYPE = {  # class: (style, weight, size px, family, extra)
    "kicker": ("italic", 800, 30, "Barlow Condensed", f"fill:{C['ink']}; letter-spacing:1px;"),
    "title": ("italic", 800, 124, "Barlow Condensed", f"fill:{C['ink']};"),
    "standfirst": ("normal", 400, 20, "Barlow", f"color:{C['ink']}; line-height:1.45;"),
    "runin": ("normal", 600, 20, "Barlow Condensed", f"color:{C['ink']}; letter-spacing:0.5px;"),
    "placename": ("normal", 600, 17, "Barlow Condensed", f"fill:{C['ink']};"),
    "ph": ("normal", 500, 15, "Barlow", f"fill:{C['muted']}; text-anchor:middle;"),
    "corner": ("normal", 500, 14, "Barlow Condensed", f"fill:{C['muted']};"),
    "callout": ("normal", 600, 17, "Barlow Condensed", f"fill:{C['ink']};"),
    "eyebrow": ("normal", 600, 15, "Barlow Condensed", f"fill:{C['muted']}; letter-spacing:1.5px;"),
    "hint": ("normal", 400, 15, "Barlow", "letter-spacing:0;"),
    "circuit": ("normal", 600, 19, "Barlow Condensed", f"fill:{C['ink']};"),
    "meta": ("normal", 400, 15, "Barlow", f"fill:{C['muted']};"),
    "axis": ("normal", 500, 14, "Barlow Condensed", f"fill:{C['muted']}; text-anchor:middle;"),
    "endlabel": ("normal", 600, 15, "Barlow Condensed", f"fill:{C['ink']};"),
    "vcard": ("normal", 400, 14.5, "Barlow", f"color:{C['ink']}; line-height:1.35;"),
    "vcard b": ("normal", 600, 19, "Barlow Condensed", "display:block; line-height:1.2; margin-bottom:3px;"),
    "vcard i": ("normal", 500, 14, "Barlow Condensed", f"color:{C['muted']}; letter-spacing:1px; margin-right:6px;"),
    "stat": ("normal", 600, 46, "Barlow", f"fill:{C['ink']};"),
    "statlabel": ("normal", 400, 16, "Barlow", f"fill:{C['muted']};"),
    "foot": ("normal", 400, 14, "Barlow", f"fill:{C['muted']};"),
}
too_small = {k: round(v[2] * PT_PER_PX, 1) for k, v in TYPE.items() if v[2] * PT_PER_PX < MIN_PT}
assert not too_small, f"text below {MIN_PT} pt in print: {too_small}"
POSTER_CSS = "\n".join(
    f".{k} {{ font:{s} {w} {px}px '{fam}'; {extra} }}" for k, (s, w, px, fam, extra) in TYPE.items()
)  # inserted as a value into the page f-string, so single braces
POSTER_CSS += "\n.badge { font-family:'Barlow Condensed'; font-weight:700; text-anchor:middle; }"

NOTES = """
<h2>Layout D, round 8</h2>
<p class="meta">140 × 85 cm at 1.6 px/mm · use <b>Zoom: Print size</b> to judge real text sizes.</p>
<h3>Latest: alignment (gestalt)</h3>
<ul>
<li><b>One shared top line</b> for the content band: the circuit band, map, key numbers and story
column all start at the same height, clearly separated from the header (proximity).</li>
<li><b>Shared bottom line:</b> the story column ends level with the positions strip.</li>
<li>The 46 logo spans from the header line to the title baseline.</li>
<li><b>Key numbers in race order</b>, each with its moment's badge: 0.730 s behind after running
wide (④), 0.002 s after lap 22 (⑥), 0.575 s winning margin (⑦). The "5 Mugello wins"
figure is gone (the poster is about 2006).</li>
</ul>
<h3>What changed</h3>
<ul>
<li><b>MUGELLO 2006</b> with the Italian livery flash sits as a header above the title.</li>
<li><b>Title: THE ROSSI COMEBACK</b>, larger now that it's shorter.</li>
<li>Then the one paragraph (event and date run in). Plain text.</li>
<li><b>Poster 5 cm taller (140 × 85 cm):</b> the extra height goes to air around the header and
a slightly larger map.</li>
<li>The QR code stays small in the bottom-right corner.</li>
</ul>
<h3>Kept from round 4</h3>
<ul><li>Livery flash after the title, no header quote, yellow stretches on the track, numbered
moments, quiet circuit card.</li></ul>
"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mugello 2006 Layout D</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;1,500;1,600;1,800&family=Barlow:ital,wght@0,400;0,500;0,600;1,400&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#121110; color:{C["ink"]}; font:15px/1.5 Barlow, system-ui, sans-serif; }}
main {{ max-width:{W + 40}px; margin:0 auto; padding:20px 16px 48px; }}
.poster svg {{ width:100%; height:auto; display:block; box-shadow:0 10px 40px #000a; }}
aside {{ background:#1E1C1B; border-radius:10px; padding:16px 22px; margin-top:20px; columns:2 340px; column-gap:40px; }}
aside h2 {{ font:700 26px 'Barlow Condensed'; margin:0 0 4px; }}
aside h3 {{ font:600 18px 'Barlow Condensed'; margin:14px 0 4px; color:#4FD1C5; break-after:avoid; }}
.meta {{ color:{C["muted"]}; font-size:13px; }}
.controls {{ display:flex; flex-wrap:wrap; gap:8px 18px; align-items:center; margin-bottom:12px; font-size:14px; color:{C["muted"]}; }}
.controls .grp {{ display:flex; gap:6px; align-items:center; flex-wrap:wrap; }}
.controls button {{ font:inherit; color:{C["ink"]}; background:#1E1C1B; border:1px solid #3A3734; border-radius:6px; padding:4px 10px; cursor:pointer; }}
.controls button[aria-pressed="true"] {{ border-color:#4FD1C5; color:#4FD1C5; }}
{POSTER_CSS}
.poster.print {{ overflow:auto; max-height:85vh; }}
.poster.print svg {{ width:140cm; max-width:none; }}
</style></head><body><main>
<div class="poster">
  <div class="controls">
    <div class="grp" data-attr="zoom" role="group" aria-label="Zoom"><span>Zoom:</span>
      <button data-v="fit" aria-pressed="true">Fit screen</button>
      <button data-v="print" aria-pressed="false">Print size (140 × 85 cm)</button></div>
    <div class="grp" data-attr="filter" role="group" aria-label="Preview"><span>Preview:</span>
      <button data-v="none" aria-pressed="true">Normal</button>
      <button data-v="url(#protan)" aria-pressed="false">Protanopia</button>
      <button data-v="url(#deutan)" aria-pressed="false">Deuteranopia</button>
      <button data-v="grayscale(1)" aria-pressed="false">Greyscale</button></div>
  </div>
  <svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
    <title id="t">Mugello 2006 poster, layout D</title>
    <desc id="d">Wide poster: Mugello map with Rossi's key moments painted yellow and numbered, circuit facts, a column of seven story cards and a strip of positions lap by lap.</desc>
    <defs>
      <filter id="protan"><feColorMatrix type="matrix" values="0.152 1.053 -0.205 0 0  0.115 0.786 0.099 0 0  -0.004 -0.048 1.052 0 0  0 0 0 1 0"/></filter>
      <filter id="deutan"><feColorMatrix type="matrix" values="0.367 0.861 -0.228 0 0  0.280 0.673 0.047 0 0  -0.012 0.043 0.969 0 0  0 0 0 1 0"/></filter>
    </defs>
    <g id="art">{"".join(svg)}</g>
  </svg>
</div>
<aside>{NOTES}</aside>
</main>
<script>
const svg = document.querySelector('.poster svg'), art = document.getElementById('art');
// place each livery flash right after its title, using the real rendered width
document.fonts.ready.then(() => {{
  document.querySelectorAll('g.flash').forEach(g => {{
    const title = document.getElementById(g.dataset.for);
    g.setAttribute('transform', `translate(${{title.getBBox().x + title.getComputedTextLength() + 14}},0)`);
  }});
}});
document.querySelectorAll('.controls .grp').forEach(g => g.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {{
  g.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
  if (g.dataset.attr === 'filter') art.style.filter = b.dataset.v;
  else if (g.dataset.attr === 'zoom') document.querySelector('.poster').classList.toggle('print', b.dataset.v === 'print');
  else svg.dataset[g.dataset.attr] = b.dataset.v;
}})));
</script>
</body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
