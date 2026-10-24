"""Generate the poster wireframe (one-off sketch tool, kept out of the repo)."""

import csv
import json
import math
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])
OUT = ROOT / "design" / "wireframe" / "poster_wireframe.html"

# A2 portrait at 2.4 px per mm
PX = 2.4
W, H = round(420 * PX), round(594 * PX)
M = round(20 * PX)

C = {
    "bg": "#1C1A19",
    "ink": "#F2EFE9",
    "muted": "#A8A29A",
    "rule": "#3A3734",
    "rossi": "#FDF504",
    "capi": "#F26B5B",
    "grey": "#6F6A64",
    "blue": "#0F8FCD",
    "green": "#229457",
    "note": "#4FD1C5",
}

POS = {
    46: [3, 1, 2, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 4, 3, 2, 2, 2, 2, 2, 1],
    65: [2, 8, 8, 8, 8, 7, 7, 7, 7, 5, 5, 4, 4, 3, 3, 1, 1, 1, 1, 1, 1, 1, 1, 2],
    69: [4, 7, 6, 5, 6, 6, 6, 6, 5, 4, 3, 3, 3, 4, 4, 3, 2, 2, 3, 3, 3, 3, 3, 3],
    15: [1, 2, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 6, 5, 5, 5, 5, 5, 5],
    33: [6, 3, 3, 3, 2, 4, 4, 3, 4, 3, 4, 5, 5, 5, 5, 4, 3, 4, 6, 6, 6, 6, 6, 6],
    26: [8, 6, 7, 7, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 5, 4, 4, 4, 4, 4, 4],
}
ROSSI_MOMENTS = {1, 4, 5, 6, 7}

moments = list(csv.DictReader((ROOT / "seeds" / "key_moments.csv").open(encoding="utf-8")))

# --- track, rotated 90 degrees so the main straight runs across like TV graphics
coords = json.loads((ROOT / "seeds" / "mugello.geojson").read_text(encoding="utf-8"))["features"][
    0
]["geometry"]["coordinates"]
k = math.cos(math.radians(coords[0][1]))
xs = [p[0] * k for p in coords]
ys = [-p[1] for p in coords]
s = 1000 / max(max(xs) - min(xs), max(ys) - min(ys))
north_up = [((x - min(xs)) * s, (y - min(ys)) * s) for x, y in zip(xs, ys, strict=True)]
tw = max(p[0] for p in north_up)
track = [(y, tw - x) for x, y in north_up]  # rotate -90deg: north points left
TRACK_W, TRACK_H = max(p[0] for p in track), max(p[1] for p in track)

MAP_TOP, MAP_H = 236, 560
scale = min((W - 2 * M - 40) / TRACK_W, (MAP_H - 40) / TRACK_H)
ox = (W - TRACK_W * scale) / 2
oy = MAP_TOP + 14


def tp(i: int) -> tuple[float, float]:
    x, y = track[i]
    return ox + x * scale, oy + y * scale


track_d = "M" + " L".join(f"{tp(i)[0]:.1f},{tp(i)[1]:.1f}" for i in range(len(track))) + " Z"
corner_idx = {
    int(r["turn"]): (r["corner_name"], int(r["point_idx"]))
    for r in csv.DictReader((ROOT / "seeds" / "corners.csv").open(encoding="utf-8"))
}

# --- shared lap axis for timeline + rank chart
X0, X1 = M + 54, W - M - 96


def lx(lap: int) -> float:
    return X0 + lap * (X1 - X0) / 23


CARDS_TOP, CARDS_H = 822, 228
AXIS_Y = 1084
RANK_TOP, ROW = 1116, 21


def ry(pos: int) -> float:
    return RANK_TOP + (pos - 1) * ROW


def badge(x: float, y: float, n: int, r: float = 13) -> str:
    rossi = n in ROSSI_MOMENTS
    fill = C["rossi"] if rossi else C["bg"]
    stroke = C["bg"] if rossi else C["ink"]
    ink = C["bg"] if rossi else C["ink"]
    return (
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="2"/><text x="{x:.1f}" y="{y + 5:.1f}" class="badge" fill="{ink}">{n}</text>'
    )


svg = []

# zone outlines (wireframe annotations)
ZONES = [
    ("A", 40, 50, 174, "Header"),
    ("B", 40, MAP_TOP - 8, MAP_H + 16, "Map"),
    ("C", 40, CARDS_TOP - 10, CARDS_H + 14, "Story"),
    ("D", 40, AXIS_Y - 22, RANK_TOP + 8 * ROW - AXIS_Y + 44, "Laps"),
    ("E", 40, 1300, 84, "Numbers"),
]
for tag, x, y, h, _ in ZONES:
    svg.append(
        f'<g class="note"><rect x="{x - 26}" y="{y}" width="{W - 2 * x + 52}" height="{h}" '
        f'rx="6" fill="none" stroke="{C["note"]}" stroke-dasharray="6 5" stroke-width="1.2"/>'
        f'<circle cx="{x - 26}" cy="{y}" r="11" fill="{C["note"]}"/>'
        f'<text x="{x - 26}" y="{y + 4.5}" class="tag">{tag}</text></g>'
    )

# A - header
svg.append(f'<text x="{M}" y="128" class="title">MUGELLO 2006</text>')
svg.append(
    f'<text x="{M + 2}" y="166" class="subtitle">Rossi vs Capirossi · Gran Premio d\'Italia · '
    f"4 June 2006</text>"
)
svg.append(
    f'<foreignObject x="{M + 2}" y="178" width="600" height="44"><div '
    f'xmlns="http://www.w3.org/1999/xhtml" class="lede">Behind in the championship, Valentino '
    f"Rossi falls from first to fifth with eight laps to go, then wins by half a second.</div>"
    f"</foreignObject>"
)
for i, label in enumerate(["46 logo", "helmet"]):
    x = W - M - 120 - i * 132
    svg.append(
        f'<rect x="{x}" y="70" width="120" height="120" rx="8" fill="none" stroke="{C["muted"]}" '
        f'stroke-dasharray="4 4"/><text x="{x + 60}" y="134" class="ph">IMAGE · {label}</text>'
    )

# B - map
svg.append(
    f'<path d="{track_d}" fill="none" stroke="{C["ink"]}" stroke-width="7" stroke-linejoin="round"/>'
)
sx, sy = tp(0)
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end")}
cxm = sum(tp(i)[0] for i in range(len(track))) / len(track)
cym = sum(tp(i)[1] for i in range(len(track))) / len(track)
svg.append(f'<rect x="{sx - 3}" y="{sy - 14}" width="6" height="28" fill="{C["green"]}"/>')
for turn, (name, idx) in corner_idx.items():
    if turn == 0:
        continue
    x, y = tp(idx)
    vx, vy = x - cxm, y - cym
    norm = math.hypot(vx, vy) or 1
    lx_, ly_ = x + vx / norm * 16, y + vy / norm * 16 + 4
    anchor = "start" if vx > 0 else "end"
    if turn in LABEL_FIX:
        fdx, fdy, anchor = LABEL_FIX[turn]
        lx_, ly_ = x + fdx, y + fdy
    svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["muted"]}"/>')
    svg.append(
        f'<text x="{lx_:.1f}" y="{ly_:.1f}" class="corner" text-anchor="{anchor}">{name}</text>'
    )
by_turn: dict[int, list[dict[str, str]]] = {}
for m in moments:
    if m["turn"]:
        by_turn.setdefault(int(m["turn"]), []).append(m)
CALLOUT = {
    0: (-100, -150, -20, 5, "end"),
    1: (-10, 104, -12, 32, "start"),
    8: (-6, -92, -12, 32, "start"),
    9: (-40, 26, -20, 5, "end"),
}
for turn, ms in by_turn.items():
    x, y = tp(corner_idx[turn][1])
    dx, dy, tdx, tdy, tanchor = CALLOUT[turn]
    for j, m in enumerate(ms):
        bx, by = x + dx + j * 30, y + dy
        svg.append(
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{C["muted"]}" stroke-width="1"/>'
        )
        svg.append(badge(bx, by, int(m["moment_id"])))
    for j, m in enumerate(ms):
        svg.append(
            f'<text x="{x + dx + tdx:.1f}" y="{y + dy + tdy + j * 17:.1f}" class="callout" '
            f'text-anchor="{tanchor}">'
            f"{m['moment_id']} · {m['headline']}</text>"
        )
svg.append(f'<text x="{sx + 10:.1f}" y="{sy - 12:.1f}" class="corner">Start / Finish</text>')
svg.append(
    f'<text x="{W - M}" y="{MAP_TOP + 24}" class="corner" text-anchor="end">'
    f"5,245 m · 15 corners · clockwise · 23 laps</text>"
)

# C - story cards
gap = 10
cw = (W - 2 * M - gap * (len(moments) - 1)) / len(moments)
for i, m in enumerate(moments):
    x = M + i * (cw + gap)
    n, lap = int(m["moment_id"]), int(m["lap"])
    accent = C["rossi"] if n in ROSSI_MOMENTS else C["grey"]
    svg.append(
        f'<rect x="{x:.1f}" y="{CARDS_TOP}" width="{cw:.1f}" height="{CARDS_H}" rx="6" fill="#262321"/>'
    )
    svg.append(f'<rect x="{x:.1f}" y="{CARDS_TOP}" width="{cw:.1f}" height="4" fill="{accent}"/>')
    svg.append(badge(x + 18, CARDS_TOP + 26, n, r=11))
    svg.append(f'<text x="{x + 36:.1f}" y="{CARDS_TOP + 31}" class="eyebrow">LAP {lap}</text>')
    svg.append(
        f'<foreignObject x="{x + 8:.1f}" y="{CARDS_TOP + 44}" width="{cw - 16:.1f}" '
        f'height="{CARDS_H - 48}"><div xmlns="http://www.w3.org/1999/xhtml" class="card">'
        f"<b>{m['headline']}</b><span>{m['story']}</span></div></foreignObject>"
    )
    cx = x + cw / 2
    svg.append(
        f'<path d="M{cx:.1f},{CARDS_TOP + CARDS_H} C{cx:.1f},{AXIS_Y - 14} {lx(lap):.1f},'
        f'{CARDS_TOP + CARDS_H + 8} {lx(lap):.1f},{AXIS_Y - 13}" fill="none" '
        f'stroke="{C["muted"]}" stroke-width="1"/>'
    )

# D - lap axis + rank chart (one shared x axis)
svg.append(
    f'<line x1="{X0}" y1="{AXIS_Y}" x2="{X1}" y2="{AXIS_Y}" stroke="{C["muted"]}" stroke-width="1"/>'
)
for lap in range(24):
    svg.append(
        f'<line x1="{lx(lap):.1f}" y1="{AXIS_Y - 4}" x2="{lx(lap):.1f}" y2="{AXIS_Y + 4}" stroke="{C["muted"]}"/>'
    )
    if lap in (0, 1, 5, 10, 15, 20, 23):
        svg.append(
            f'<text x="{lx(lap):.1f}" y="{AXIS_Y + 18}" class="axis">{"Grid" if lap == 0 else lap}</text>'
        )
svg.append(f'<text x="{X0 - 16}" y="{AXIS_Y + 4}" class="axis" text-anchor="end">LAP</text>')
for m in moments:
    lap = int(m["lap"])
    svg.append(
        f'<line x1="{lx(lap):.1f}" y1="{AXIS_Y + 22}" x2="{lx(lap):.1f}" y2="{ry(8) + 8}" stroke="{C["rule"]}" stroke-width="1"/>'
    )
    svg.append(badge(lx(lap), AXIS_Y, int(m["moment_id"]), r=10))
for pos in range(1, 9):
    svg.append(
        f'<text x="{X0 - 10}" y="{ry(pos) + 4:.1f}" class="axis" text-anchor="end">{pos}{"st" if pos == 1 else "nd" if pos == 2 else "rd" if pos == 3 else "th"}</text>'
    )


def poly(n: int) -> str:
    return " ".join(f"{lx(i):.1f},{ry(p):.1f}" for i, p in enumerate(POS[n]))


for n in (69, 15, 33, 26):
    svg.append(
        f'<polyline points="{poly(n)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5" stroke-linejoin="round"/>'
    )
svg.append(
    f'<polyline points="{poly(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3" stroke-linejoin="round"/>'
)
svg.append(
    f'<polyline points="{poly(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7" stroke-linejoin="round"/>'
)
svg.append(
    f'<polyline points="{poly(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4" stroke-linejoin="round"/>'
)
for n, label, color in ((46, "Rossi · 1st", C["rossi"]), (65, "Capirossi · 2nd", C["capi"])):
    y = ry(POS[n][-1])
    svg.append(
        f'<circle cx="{lx(23):.1f}" cy="{y:.1f}" r="5" fill="{color}" stroke="{C["bg"]}" stroke-width="2"/>'
    )
    svg.append(f'<text x="{lx(23) + 12:.1f}" y="{y + 4:.1f}" class="endlabel">{label}</text>')
svg.append(
    f'<text x="{lx(23) + 12:.1f}" y="{ry(3) + 4:.1f}" class="axis" text-anchor="start">others</text>'
)

# E - key numbers + credits
STATS = [
    ("0.575 s", "Rossi's winning margin"),
    ("0.002 s", "between them after lap 22"),
    ("5", "Mugello wins in a row"),
]
tile_w = (W - 2 * M) / 3
for i, (value, label) in enumerate(STATS):
    x = M + i * tile_w
    svg.append(f'<text x="{x:.1f}" y="1342" class="stat">{value}</text>')
    svg.append(f'<text x="{x + 2:.1f}" y="1364" class="statlabel">{label}</text>')
svg.append(
    f'<text x="{M}" y="{H - 22}" class="credit">Data: official MotoGP timing (Tissot / Dorna). '
    f"Track outline: bacinger/f1-circuits (MIT). Story: MotoGP race broadcast; Paddock Pass "
    f"Podcast.</text>"
)

notes = """
<h2>Design notes</h2>
<p class="meta">Mid-fidelity wireframe · A2 portrait (420 × 594 mm) at 2.4 px/mm ·
real data, final colours, draft copy · images are placeholders.</p>
<ol class="zones">
<li><b>A · Header.</b> Title, one-line subtitle, and a <i>lede</i>: the whole story in one
sentence for someone who reads nothing else. The 46 logo and the helmet sit top-right as images.</li>
<li><b>B · Map (the hero).</b> Mugello turned 90° like TV graphics, so the main straight runs
across. Only the corners where something happened get a numbered badge.
<span class="y">Yellow badge</span> = a Rossi moment, outlined badge = context
(e.g. Stoner's crash). The green bar marks the finish line. All 15 corner names are kept small
because the track itself is a protagonist.</li>
<li><b>C · Story cards.</b> One card per key moment, in lap order: lap, headline, two or three
plain sentences (≤ 200 characters, enforced by a test). A thin curve leads from each card to its
lap on the axis.</li>
<li><b>D · Laps + positions.</b> One shared lap axis (grid → lap 23). The badges sit on the axis
and faint guides drop into the position chart below. Position chart: 1st at the top, only the
leading 6 riders, Rossi thick yellow, Capirossi coral, everyone else thin grey and unlabelled.
Labels at the line ends name both riders, so colour is never the only cue.</li>
<li><b>E · Key numbers.</b> Three big figures with a plain label each. Same font as everything
else, proportional digits. Credits line (required by the track licence).</li>
</ol>
<h3>Reading path</h3>
<p>Title → lede → map badges → cards ① to ⑦ → the yellow line falling to 5th and climbing back → the three numbers.</p>
<h3>Open questions</h3>
<ul>
<li>Map orientation: rotated (as here) or north-up? Tableau maps can't rotate, so the rotated
version needs x/y coordinates from the pipeline instead of a map.</li>
<li>Card 2 (Stoner) and card 3 (Capirossi's charge): keep both, or cut to 5 cards for more air?</li>
<li>Title wording, and whether to add a dedication line for your dad.</li>
</ul>
"""

controls = """
<div class="controls" role="group" aria-label="Preview mode">
  <span>Preview as:</span>
  <button data-f="none" aria-pressed="true">Normal vision</button>
  <button data-f="url(#protan)" aria-pressed="false">Protanopia</button>
  <button data-f="url(#deutan)" aria-pressed="false">Deuteranopia</button>
  <button data-f="grayscale(1)" aria-pressed="false">Greyscale print</button>
  <label><input type="checkbox" id="notes" checked> Zone outlines</label>
</div>
"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mugello 2006 Wireframe</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;1,800&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>
:root {{ --page:#121110; --panel:#1E1C1B; --ink:{C["ink"]}; --muted:{C["muted"]}; --note:{C["note"]}; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--page); color:var(--ink); font:15px/1.5 Barlow, system-ui, sans-serif; }}
.wrap {{ display:flex; gap:32px; padding:24px 16px; justify-content:center; flex-wrap:wrap; }}
.poster {{ flex:0 1 {W}px; min-width:0; }}
.poster svg {{ width:100%; height:auto; display:block; box-shadow:0 10px 40px #000a; }}
aside {{ flex:0 1 380px; background:var(--panel); border-radius:10px; padding:20px 22px; align-self:flex-start; }}
aside h2 {{ font:700 26px 'Barlow Condensed'; margin:0 0 4px; }}
aside h3 {{ font:600 18px 'Barlow Condensed'; margin:18px 0 4px; color:var(--note); }}
.meta {{ color:var(--muted); font-size:13px; }}
.zones li {{ margin-bottom:10px; }}
.y {{ background:{C["rossi"]}; color:{C["bg"]}; padding:0 4px; border-radius:3px; }}
.controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px; font-size:14px; color:var(--muted); }}
.controls button {{ font:inherit; color:var(--ink); background:var(--panel); border:1px solid #3A3734; border-radius:6px; padding:4px 10px; cursor:pointer; }}
.controls button[aria-pressed="true"] {{ border-color:var(--note); color:var(--note); }}
.title {{ font:italic 800 82px 'Barlow Condensed'; fill:{C["ink"]}; letter-spacing:1px; }}
.subtitle {{ font:500 24px 'Barlow Condensed'; fill:{C["ink"]}; }}
.lede {{ font:400 15px/1.35 Barlow; color:{C["muted"]}; }}
.ph {{ font:500 11px Barlow; fill:{C["muted"]}; text-anchor:middle; }}
.corner {{ font:500 11px 'Barlow Condensed'; fill:{C["muted"]}; }}
.callout {{ font:600 14px 'Barlow Condensed'; fill:{C["ink"]}; }}
.badge {{ font:700 13px 'Barlow Condensed'; text-anchor:middle; }}
.eyebrow {{ font:600 12px 'Barlow Condensed'; fill:{C["muted"]}; letter-spacing:1.5px; }}
.card {{ font:400 11.5px/1.35 Barlow; color:{C["ink"]}; }}
.card b {{ display:block; font:600 15px/1.15 'Barlow Condensed'; margin-bottom:4px; }}
.axis {{ font:500 11px 'Barlow Condensed'; fill:{C["muted"]}; text-anchor:middle; }}
.endlabel {{ font:600 13px 'Barlow Condensed'; fill:{C["ink"]}; }}
.stat {{ font:600 44px Barlow; fill:{C["ink"]}; }}
.statlabel {{ font:400 13px Barlow; fill:{C["muted"]}; }}
.credit {{ font:400 8.5px Barlow; fill:{C["muted"]}; }}
.tag {{ font:700 12px Barlow; fill:#0B2B28; text-anchor:middle; }}
.hide-notes .note {{ display:none; }}
</style></head>
<body>
<div class="wrap">
  <div class="poster">
    {controls}
    <svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
      <title id="t">Mugello 2006 poster wireframe</title>
      <desc id="d">Map of Mugello with seven numbered moments, story cards, a lap axis and a position chart showing Rossi falling to fifth on lap 15 and winning on lap 23.</desc>
      <defs>
        <filter id="protan"><feColorMatrix type="matrix" values="0.152 1.053 -0.205 0 0  0.115 0.786 0.099 0 0  -0.004 -0.048 1.052 0 0  0 0 0 1 0"/></filter>
        <filter id="deutan"><feColorMatrix type="matrix" values="0.367 0.861 -0.228 0 0  0.280 0.673 0.047 0 0  -0.012 0.043 0.969 0 0  0 0 0 1 0"/></filter>
      </defs>
      <g id="art"><rect width="{W}" height="{H}" fill="{C["bg"]}"/>
      {"".join(svg)}</g>
    </svg>
  </div>
  <aside>{notes}</aside>
</div>
<script>
const art = document.getElementById('art');
document.querySelectorAll('.controls button').forEach(b => b.addEventListener('click', () => {{
  document.querySelectorAll('.controls button').forEach(x => x.setAttribute('aria-pressed', x === b));
  art.style.filter = b.dataset.f;
}}));
document.getElementById('notes').addEventListener('change', e =>
  document.querySelector('.poster svg').classList.toggle('hide-notes', !e.target.checked));
</script>
</body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
