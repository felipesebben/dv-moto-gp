"""Refined wireframe for layout D (120 cm wide, built on a 4 px spacing grid).

Run: uv run python design/wireframe/tools/build_poster_d.py
Writes design/wireframe/poster_d.html. Sketch tool only: the real poster is built in Tableau.
Event facts below are copied from the official classification PDF and the track GeoJSON;
the build will read them from the pipeline instead.
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sketchlib import (  # noqa: E402
    C, CONTEXT, POS, RIVAL_MOMENTS, ROSSI_MOMENTS, badge, fit, load, ordinal, path, position_at,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "design" / "wireframe" / "poster_d.html"
track, corners, moments = load(ROOT)
ITALY = {"green": "#229457", "white": C["ink"], "red": "#CE2B37"}  # flag red, kept apart from Capirossi's coral

# ---- spacing system ----------------------------------------------------------------------
# Every layout position, size, gap and padding is a multiple of 4 px, taken from these steps.
# Proximity: gaps inside a group (8-24) are always smaller than gaps between sections (64), and
# the two big breaks (header -> map band -> race band) get 128 for air.
U = 4
XS, S_, M_, L_, XL, XXL, PAD, BREAK = 8, 16, 24, 32, 48, 64, 96, 128  # the only spacing steps used


def snap(v: float) -> int:
    return round(v / U) * U


PX = 1.6  # px per mm in this sketch (print: 1 px = 0.625 mm)
W = 1920  # 120 cm wide
LEFT, RIGHT = PAD, W - PAD  # shared left and right edges for every band
LAYOUT: dict[str, float] = {"W": W, "PAD": PAD}  # checked against the 4 px grid at the end

# ---- header: kicker, title, then the paragraph on longer lines; all on the left edge ----
KICKER_Y = PAD + M_  # baselines
TITLE_Y = KICKER_Y + M_ + 96
STAND_Y = TITLE_Y + L_  # paragraph box top
STAND_W, STAND_LINES, STAND_LH = 1408, 3, 28  # three longer lines under the title
HEADER_BOTTOM = STAND_Y + STAND_LINES * STAND_LH
LAYOUT |= {"KICKER_Y": KICKER_Y, "TITLE_Y": TITLE_Y, "STAND_Y": STAND_Y, "STAND_W": STAND_W,
           "HEADER_BOTTOM": HEADER_BOTTOM}

# ---- map band: circuit facts (bottom-left) · map (centre) · key numbers (top-right) ----------
BAND_TOP = HEADER_BOTTOM + BREAK
MAP_H = 800  # grows with the poster so the map's share of it never shrinks
MAP_W = snap(MAP_H * 1000 / 705)  # the track's aspect ratio in TV orientation
MAP_X, MAP_Y = snap((W - MAP_W) / 2), BAND_TOP + M_  # corner labels sit in the 24 px above
BAND_BOTTOM = MAP_Y + MAP_H
COL_L_W = MAP_X - L_ - LEFT  # left column: Italy + circuit facts
COL_R_X = MAP_X + MAP_W + L_  # right column: key numbers
LAYOUT |= {"BAND_TOP": BAND_TOP, "MAP_X": MAP_X, "MAP_Y": MAP_Y, "MAP_W": MAP_W, "MAP_H": MAP_H,
           "BAND_BOTTOM": BAND_BOTTOM, "COL_L_W": COL_L_W, "COL_R_X": COL_R_X}

# ---- race band ------------------------------------------------------------------------------
RACE_TOP = BAND_BOTTOM + BREAK  # eyebrow baseline
CARD_H, CARD_MAX, CARD_MIN, CARD_GAP = 128, 472, 264, M_
TOP_CARDS = RACE_TOP + M_
AXIS_Y = TOP_CARDS + CARD_H + L_
ROW = S_
X0, X1 = LEFT + XXL, RIGHT - CARD_MIN  # one narrow card fits after lap 23: every line stays vertical
CHART_BOTTOM = AXIS_Y + M_ + 7 * ROW
BOTTOM_CARDS = CHART_BOTTOM + XL
QR_S = XXL  # 40 mm in print: easy to scan
FOOT_Y = BOTTOM_CARDS + 96 + XL + QR_S  # footer baseline (cards below the chart run 2-3 lines)
H = FOOT_Y + PAD
LAYOUT |= {"RACE_TOP": RACE_TOP, "CARD_H": CARD_H, "TOP_CARDS": TOP_CARDS, "AXIS_Y": AXIS_Y,
           "X0": X0, "X1": X1, "CHART_BOTTOM": CHART_BOTTOM, "BOTTOM_CARDS": BOTTOM_CARDS,
           "FOOT_Y": FOOT_Y, "H": H}

svg: list[str] = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']

# ---- header ---------------------------------------------------------------------------------
svg.append(f'<text id="kicker" x="{LEFT}" y="{KICKER_Y}" class="kicker">MUGELLO 2006</text>')
# drawn at x=0; the page script moves it to the measured end of the kicker
svg.append('<g class="flash" data-for="kicker">' + "".join(
    f'<polygon points="{i * 10 + 12},{KICKER_Y - 24} {i * 10 + 18},{KICKER_Y - 24} '
    f'{i * 10 + 6},{KICKER_Y} {i * 10},{KICKER_Y}" fill="{c}"/>'
    for i, c in enumerate(ITALY.values())
) + "</g>")
svg.append(f'<text x="{LEFT - 6}" y="{TITLE_Y}" class="title">THE ROSSI COMEBACK</text>')  # -6: optical alignment of the italic T
svg.append(
    f'<foreignObject x="{LEFT}" y="{STAND_Y}" width="{STAND_W}" height="{STAND_LINES * STAND_LH + XS}">'
    f'<div xmlns="http://www.w3.org/1999/xhtml" class="standfirst">'
    f"<span class=\"runin\">Gran Premio d&#8217;Italia Alice, 4 June 2006.</span> "
    f"Forty-three points down in the championship and in front of his home crowd, Valentino Rossi "
    f"was leading when he ran wide at San Donato and fell to fifth, with eight laps left. He hunted "
    f"Loris Capirossi down lap after lap and, on the final lap, passed him for the win at the same "
    f"corner. Patience, then one perfect move: a race still counted among his greatest."
    f"</div></foreignObject>"
)

# ---- map ----------------------------------------------------------------------------------
pts = fit(track, MAP_X, MAP_Y, MAP_W, MAP_H)
SCALE = MAP_H / 705
CALLOUT = {0: (-136, -204, -20, 5, "end"), 1: (-14, 141, -12, 32, "start"),
           8: (-8, -125, -12, 32, "start")}
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end"),
             12: (-12, 5, "end")}  # Correntaio to the left of its loop
STRETCHES = [range(7, 14), range(57, 65), [*range(125, 129), 0]]
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
    lx_, ly_, anchor = x + vx / n * 16, y + vy / n * 16 + 4, "start" if vx > 0 else "end"
    if turn in LABEL_FIX:
        dx, dy, anchor = LABEL_FIX[turn]
        lx_, ly_ = x + dx, y + dy
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["muted"]}"/>')
    svg.append(f'<text x="{lx_:.1f}" y="{ly_:.1f}" class="corner" text-anchor="{anchor}">{name}</text>')
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

# ---- left column: Italy + the circuit facts, bottom-aligned with the map ----------------------
# (circuit information + classification PDFs; name and town from the track GeoJSON;
# Italy outline from Natural Earth, public domain)
italy = json.loads((ROOT / "seeds" / "italy.geojson").read_text(encoding="utf-8"))
kx = math.cos(math.radians(42))
rings = [[(lon * kx, -lat) for lon, lat in poly[0]] for poly in italy["features"][0]["geometry"]["coordinates"]]
allx = [x for r in rings for x, _ in r]
ally = [y for r in rings for _, y in r]
FACTS = [  # short lines: the column is narrow
    "Scarperia e San Piero, Tuscany",
    "Built 1974 · 5,245 m · 14 m wide",
    "15 corners: 9 right, 6 left",
    "Longest straight 1,141 m",
    "Race: 23 laps · 120.6 km",
    "Dry · air 20 °C · track 29 °C",
]
ITALY_BOX, LINE = 232, M_
col_top = BAND_BOTTOM - (S_ + S_ + ITALY_BOX + M_ + 2 * LINE + XS + len(FACTS) * LINE)
LAYOUT |= {"col_top": col_top, "ITALY_BOX": ITALY_BOX}
svg.append(f'<text x="{LEFT}" y="{col_top + 12}" class="eyebrow">THE CIRCUIT</text>')
box_y = col_top + S_ + S_
isc = min(ITALY_BOX / (max(allx) - min(allx)), ITALY_BOX / (max(ally) - min(ally)))


def ip(x: float, y: float) -> tuple[float, float]:
    return LEFT + (x - min(allx)) * isc, box_y + (y - min(ally)) * isc


for r in rings:
    svg.append(f'<path d="{path([ip(x, y) for x, y in r], True)}" fill="#2A2725" stroke="{C["muted"]}" stroke-width="1.2" stroke-linejoin="round"/>')
mx, my = ip(11.372 * kx, -43.997)  # Mugello
svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="9" fill="none" stroke="{C["rossi"]}" stroke-width="2"/>')
svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="3.5" fill="{C["rossi"]}"/>')
svg.append(f'<text x="{mx + 16:.1f}" y="{my + 6:.1f}" class="placename">Mugello</text>')
name_y = box_y + ITALY_BOX + M_ + 16  # baseline of the first name line
svg.append(f'<text x="{LEFT}" y="{name_y}" class="circuit">Autodromo Internazionale</text>')
svg.append(f'<text x="{LEFT}" y="{name_y + LINE}" class="circuit">del Mugello</text>')
for i, line in enumerate(FACTS):
    svg.append(f'<text x="{LEFT}" y="{name_y + 2 * LINE + XS + i * LINE}" class="meta">{line}</text>')

# ---- right column: key numbers, top-aligned with the map, in race order --------------------
STATS = [  # (value, label lines, badge); values from poster.timeline
    ("0.730 s", ["behind Capirossi after running", "wide, in 5th"], 4),
    ("0.002 s", ["between them after lap 22"], 6),
    ("0.575 s", ["Rossi&#8217;s winning margin"], 7),
]
STAT_STEP = 104
for i, (v, label, n) in enumerate(STATS):
    y = MAP_Y + 36 + i * STAT_STEP  # number baseline: its cap height starts on the map's top
    svg.append(badge(COL_R_X + 10, y - 16, n, r=10))
    svg.append(f'<text x="{COL_R_X + L_}" y="{y}" class="stat">{v}</text>')
    for j, part in enumerate(label):
        svg.append(f'<text x="{COL_R_X + L_ + 2}" y="{y + M_ + j * 20}" class="statlabel">{part}</text>')
LAYOUT |= {"STAT_STEP": STAT_STEP}

# ---- race band: positions chart with the moments along it --------------------------------
# Moments alternate above (laps 1, 13, 18, 23) and below (laps 7, 15, 22) the chart so close
# laps don't collide. Each card starts exactly at its lap with its number beside the text, and a
# thin straight line drops from the number to where the rider was on that lap (Rossi's moments
# to Rossi's line, Capirossi's to his). The chart stops one narrow card short of the right edge
# so the last moments still start at their lap and every line stays vertical.


def lx(lap: float) -> float:
    return X0 + lap * (X1 - X0) / 23


def ry(pos: float) -> float:
    return AXIS_Y + M_ + (pos - 1) * ROW


svg.append(f'<text x="{LEFT}" y="{RACE_TOP}" class="eyebrow">THE RACE, LAP BY LAP <tspan class="hint">· each line is a rider, higher = further ahead · numbers match the map</tspan></text>')
svg.append(f'<line x1="{X0}" y1="{AXIS_Y}" x2="{X1}" y2="{AXIS_Y}" stroke="{C["muted"]}"/>')
for lap in range(24):
    svg.append(f'<line x1="{lx(lap):.1f}" y1="{AXIS_Y - 4}" x2="{lx(lap):.1f}" y2="{AXIS_Y + 4}" stroke="{C["muted"]}"/>')
svg.append(f'<text x="{X0 - S_}" y="{AXIS_Y + 4}" class="axis" text-anchor="end">Grid</text>')
for p_ in (1, 4, 8):
    svg.append(f'<text x="{X0 - S_}" y="{ry(p_) + 4:.1f}" class="axis" text-anchor="end">{ordinal(p_)}</text>')
svg.append(f'<text x="{X1:.1f}" y="{CHART_BOTTOM + M_}" class="axis">Lap 23</text>')

tiers = {"above": [m for i, m in enumerate(moments) if i % 2 == 0],
         "below": [m for i, m in enumerate(moments) if i % 2 == 1]}
cards = []
for side, ms in tiers.items():
    lefts = [lx(int(m["lap"])) for m in ms]
    rights = [min(lefts[i + 1] - CARD_GAP if i + 1 < len(ms) else RIGHT, lefts[i] + CARD_MAX)
              for i in range(len(ms))]
    cards += [(side, m, left, right) for m, left, right in zip(ms, lefts, rights, strict=True)]


def colour_of(n: int) -> str:
    return C["rossi"] if n in ROSSI_MOMENTS else C["capi"] if n in RIVAL_MOMENTS else C["grey"]


def anchor(n: int, lap: int) -> tuple[float, float]:
    """Where the moment's rider was on the chart at that lap."""
    return lx(lap), ry(POS[65 if n in RIVAL_MOMENTS else 46][lap])


for side, m, left, right in cards:  # under the riders' lines
    n, lap = int(m["moment_id"]), int(m["lap"])
    ax, ay = anchor(n, lap)
    by = TOP_CARDS + M_ if side == "above" else BOTTOM_CARDS  # the badge's edge nearest the chart
    svg.append(f'<line x1="{left:.1f}" y1="{by:.1f}" x2="{ax:.1f}" y2="{ay:.1f}" stroke="{colour_of(n)}" stroke-width="1.5" stroke-opacity="0.85"/>')


def hline(r: int) -> str:
    return " ".join(f"{lx(t / 10):.1f},{ry(position_at(POS[r], t / 10)):.1f}" for t in range(231))


for r in CONTEXT:
    svg.append(f'<polyline points="{hline(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>')
svg.append(f'<polyline points="{hline(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>')
for r, label in ((46, "Rossi · 1st"), (65, "Capirossi · 2nd")):
    y = ry(POS[r][-1])
    svg.append(f'<circle cx="{lx(23):.1f}" cy="{y:.1f}" r="5" fill="{C["rossi"] if r == 46 else C["capi"]}" stroke="{C["bg"]}" stroke-width="2"/>')
    svg.append(f'<text x="{lx(23) + S_:.1f}" y="{y + 4:.1f}" class="endlabel">{label}</text>')

for side, m, left, right in cards:
    n, lap = int(m["moment_id"]), int(m["lap"])
    y = TOP_CARDS if side == "above" else BOTTOM_CARDS
    svg.append(badge(left, y + 12, n, r=12))  # the number, beside the text
    svg.append(
        f'<foreignObject x="{left + M_:.1f}" y="{y - 2}" width="{right - left - M_:.1f}" height="{CARD_H + 4}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="vcard"><b><i>LAP {lap}</i> {m["headline"]}</b>'
        f'<span>{m["story"]}</span></div></foreignObject>'
    )
    ax, ay = anchor(n, lap)
    svg.append(f'<circle cx="{ax:.1f}" cy="{ay:.1f}" r="5" fill="{colour_of(n)}" stroke="{C["bg"]}" stroke-width="2"/>')  # the rider, that lap

# ---- footer: map key (left edge) + credits and QR (right edge) -----------------------------
KEY = [("badge", 4, "Rossi moment"), ("badge", 2, "Capirossi moment"), ("line", 0, "where it happened")]
kx_ = LEFT
for kind, n, text in KEY:
    if kind == "badge":
        svg.append(badge(kx_ + 10, FOOT_Y - 5, n, r=10))
    else:
        svg.append(f'<line x1="{kx_}" y1="{FOOT_Y - 5}" x2="{kx_ + 20}" y2="{FOOT_Y - 5}" stroke="{C["rossi"]}" stroke-width="6" stroke-linecap="round"/>')
    svg.append(f'<text x="{kx_ + L_}" y="{FOOT_Y}" class="foot">{text}</text>')
    kx_ += L_ + len(text) * 8 + XL  # label width estimate (14 px Barlow) + a 48 px gap
qr = (ROOT / "design" / "wireframe" / "assets" / "qr_full_race.svg").read_text(encoding="utf-8")
qr = qr.replace('<svg xmlns="http://www.w3.org/2000/svg" width="37" height="37"',
                f'<svg x="{RIGHT - QR_S}" y="{FOOT_Y - QR_S + 4}" width="{QR_S}" height="{QR_S}" viewBox="0 0 37 37"', 1)
svg.append(qr)
svg.append(f'<text x="{RIGHT - QR_S - M_}" y="{FOOT_Y - L_}" class="foot" text-anchor="end">Watch the race</text>')
svg.append(
    f'<text x="{RIGHT - QR_S - M_}" y="{FOOT_Y}" class="foot" text-anchor="end">Data: official MotoGP timing (Tissot / Dorna) · '
    f"Track: bacinger/f1-circuits (MIT) · Story: MotoGP broadcast, Paddock Pass Podcast</text>"
)

# ---- the map stays the main actor: its share of the poster never drops below the approved 22 % --
MAP_SHARE = MAP_W * MAP_H / (W * H)
assert MAP_SHARE >= 0.22, f"map shrank to {MAP_SHARE:.1%} of the poster"

# ---- the grid rule: every layout position and size is a multiple of 4 px --------------------
off_grid = {k: v for k, v in LAYOUT.items() if v % U}
assert not off_grid, f"layout values off the 4 px grid: {off_grid}"


# ---- type scale (px at 1.6 px/mm; 1 px = 1.77 pt in print). Nothing below MIN_PT. ----
PT_PER_PX = 72 / 25.4 / PX
MIN_PT = 24  # our floor for anything on the poster (the hard rule is 10 pt)
TYPE = {  # class: (style, weight, size px, family, extra)
    "kicker": ("italic", 800, 30, "Barlow Condensed", f"fill:{C['ink']}; letter-spacing:1px;"),
    "title": ("italic", 800, 124, "Barlow Condensed", f"fill:{C['ink']};"),
    "standfirst": ("normal", 400, 20, "Barlow", f"color:{C['ink']}; line-height:{STAND_LH}px;"),
    "runin": ("normal", 600, 20, "Barlow Condensed", f"color:{C['ink']}; letter-spacing:0.5px;"),
    "placename": ("normal", 600, 17, "Barlow Condensed", f"fill:{C['ink']};"),
    "corner": ("normal", 500, 14, "Barlow Condensed", f"fill:{C['muted']};"),
    "callout": ("normal", 600, 17, "Barlow Condensed", f"fill:{C['ink']};"),
    "eyebrow": ("normal", 600, 15, "Barlow Condensed", f"fill:{C['muted']}; letter-spacing:1.5px;"),
    "hint": ("normal", 400, 15, "Barlow", "letter-spacing:0;"),
    "circuit": ("normal", 600, 19, "Barlow Condensed", f"fill:{C['ink']};"),
    "meta": ("normal", 400, 15, "Barlow", f"fill:{C['muted']};"),
    "axis": ("normal", 500, 14, "Barlow Condensed", f"fill:{C['muted']}; text-anchor:middle;"),
    "endlabel": ("normal", 600, 15, "Barlow Condensed", f"fill:{C['ink']};"),
    "vcard": ("normal", 400, 14.5, "Barlow", f"color:{C['ink']}; line-height:20px;"),
    "vcard b": ("normal", 600, 19, "Barlow Condensed", "display:block; line-height:24px; margin-bottom:4px;"),
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
<h2>Layout D, round 17: rebuilt on a spacing grid</h2>
<p class="meta">120 cm wide at 1.6 px/mm · use <b>Zoom: Print size</b> to judge real text sizes.</p>
<ul>
<li><b>4 px spacing grid:</b> every block position, gap and padding uses 8 · 16 · 24 · 32 · 48 · 64 · 96;
the generator refuses to build otherwise. Poster padding 96 px (60 mm) on every side.</li>
<li><b>Proximity:</b> gaps inside a group (8–24) are always smaller than gaps between sections (64).</li>
<li><b>Alignment:</b> one left edge for the kicker, title, paragraph, circuit column, race band and
footer; one right edge for the key numbers, the moments and the footer; the map centred.</li>
<li>Narrower poster (120 cm). The paragraph sits under the title on longer lines (3 lines).</li>
<li>Map centred again, between Italy + circuit facts (bottom-left) and the key numbers (top-right).</li>
</ul>
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
.poster.print svg {{ width:120cm; max-width:none; }}
</style></head><body><main>
<div class="poster">
  <div class="controls">
    <div class="grp" data-attr="zoom" role="group" aria-label="Zoom"><span>Zoom:</span>
      <button data-v="fit" aria-pressed="true">Fit screen</button>
      <button data-v="print" aria-pressed="false">Print size (120 cm wide)</button></div>
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
