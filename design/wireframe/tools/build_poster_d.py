"""Refined wireframe for layout D (100 x 70 cm landscape).

Run: uv run python design/wireframe/tools/build_poster_d.py
Writes design/wireframe/poster_d.html. Sketch tool only: the real poster is built in Tableau.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sketchlib import (
    CONTEXT,
    POS,
    ROSSI_MOMENTS,
    C,
    badge,
    fit,
    load,
    ordinal,
    path,
    position_at,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "design" / "wireframe" / "poster_d.html"
track, corners, moments = load(ROOT)

PX = 1.6  # px per mm
W, H = round(1000 * PX), round(700 * PX)
M = 88  # 55 mm margin: the poster breathes
COL = 1150  # story column starts here
GUTTER_R = W - M

# ---- map placement ------------------------------------------------------------
MAP = (M, 296, 1000 - M + 40, 516)  # x, y, w, h
pts = fit(track, *MAP)
SCALE = MAP[3] / 705  # track units -> px (height-bound)

# callouts: badge offset in track units; text offset in px; anchor
CALLOUT = {
    0: (-136, -204, -20, 5, "end"),
    1: (-14, 141, -12, 32, "start"),
    8: (-8, -125, -12, 32, "start"),
    9: (-54, 35, -20, 5, "end"),
}
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end")}
# outline point ranges where Rossi's moments happened (painted yellow)
STRETCHES = {
    "San Donato braking (laps 15, 23)": range(7, 14),
    "Savelli to Arrabbiata 1 (lap 18)": range(57, 65),
    "Main straight (laps 1, 22)": [*range(125, 129), 0],
}

svg: list[str] = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
notes: list[tuple[str, float, float, float, float]] = []  # tag, x, y, w, h


def zone(tag: str, x: float, y: float, w: float, h: float) -> None:
    notes.append((tag, x, y, w, h))


# ---- header -------------------------------------------------------------------
svg.append(f'<text x="{M - 4}" y="160" class="title">MUGELLO 2006</text>')
svg.append(
    f'<text x="{M}" y="200" class="subtitle">Rossi vs Capirossi · Gran Premio d&#8217;Italia · 4 June 2006</text>'
)
svg.append(
    f'<foreignObject x="{M}" y="212" width="700" height="56"><div xmlns="http://www.w3.org/1999/xhtml" '
    f'class="lede">Behind in the championship, Valentino Rossi falls from first to fifth with eight '
    f"laps to go, then wins by half a second.</div></foreignObject>"
)
zone("A", M - 10, 88, 760, 196)

# ---- images (right column top) ------------------------------------------------
for i, label in enumerate(["helmet", "46 logo"]):
    x = COL + i * 196
    svg.append(
        f'<rect x="{x}" y="{M}" width="166" height="150" rx="8" fill="none" stroke="{C["muted"]}" stroke-dasharray="4 4"/>'
    )
    svg.append(f'<text x="{x + 83}" y="{M + 79}" class="ph">IMAGE · {label}</text>')
zone("B", COL - 10, M - 10, GUTTER_R - COL + 20, 170)

# ---- map ------------------------------------------------------------------------
svg.append(
    f'<path d="{path(pts, True)}" fill="none" stroke="{C["ink"]}" stroke-width="7" stroke-linejoin="round"/>'
)
for seg in STRETCHES.values():
    svg.append(
        f'<path d="{path([pts[i] for i in seg])}" fill="none" stroke="{C["rossi"]}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
    )
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
    svg.append(
        f'<text x="{lx:.1f}" y="{ly:.1f}" class="corner" text-anchor="{anchor}">{name}</text>'
    )
by_turn: dict[int, list[dict[str, str]]] = {}
for m in moments:
    if m["turn"]:
        by_turn.setdefault(int(m["turn"]), []).append(m)
for turn, ms in by_turn.items():
    x, y = pts[corners[turn][1]]
    ux, uy, tdx, tdy, anchor = CALLOUT[turn]
    bx, by = x + ux * SCALE, y + uy * SCALE
    for j, m in enumerate(ms):
        svg.append(
            f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx + j * 30:.1f}" y2="{by:.1f}" stroke="{C["muted"]}" stroke-width="1"/>'
        )
        svg.append(badge(bx + j * 30, by, int(m["moment_id"])))
    for j, m in enumerate(ms):
        svg.append(
            f'<text x="{bx + tdx:.1f}" y="{by + tdy + j * 18:.1f}" class="callout" text-anchor="{anchor}">{m["moment_id"]} · {m["headline"]}</text>'
        )
zone("C", MAP[0] - 10, MAP[1] - 6, MAP[2] + 20, MAP[3] + 54)

# map key, in the empty bottom-left of the map area
kx, ky = M, 724
svg.append(f'<text x="{kx}" y="{ky}" class="eyebrow">HOW TO READ THE MAP</text>')
svg.append(badge(kx + 10, ky + 24, 4, r=10))
svg.append(
    f'<text x="{kx + 28}" y="{ky + 29}" class="key">a Rossi moment (the number matches its story)</text>'
)
svg.append(badge(kx + 10, ky + 50, 2, r=10))
svg.append(f'<text x="{kx + 28}" y="{ky + 55}" class="key">another moment of the race</text>')
svg.append(
    f'<line x1="{kx}" y1="{ky + 76}" x2="{kx + 20}" y2="{ky + 76}" stroke="{C["rossi"]}" stroke-width="7" stroke-linecap="round"/>'
)
svg.append(
    f'<text x="{kx + 28}" y="{ky + 81}" class="key">where on the track Rossi&#8217;s moments happened</text>'
)

# key numbers, in the empty top-right of the map area, each tied to its moment
STATS = [
    ("0.575 s", "Rossi&#8217;s winning margin", 7),
    ("0.002 s", "between them after lap 22", 6),
    ("5", "Mugello wins in a row", None),
]
for i, (v, label, n) in enumerate(STATS):
    y = 344 + i * 66
    svg.append(f'<text x="896" y="{y}" class="stat">{v}</text>')
    svg.append(f'<text x="898" y="{y + 22}" class="statlabel">{label}</text>')
    if n:
        svg.append(badge(878, y - 16, n, r=9))
zone("D", 866, 296, 220, 206)

# ---- story column ---------------------------------------------------------------
top, slot = 290, 106
svg.append(
    f'<line x1="{COL + 12}" y1="{top + 28}" x2="{COL + 12}" y2="{top + 6 * slot + 28}" stroke="{C["rule"]}" stroke-width="2"/>'
)
for i, m in enumerate(moments):
    y = top + i * slot
    n = int(m["moment_id"])
    svg.append(badge(COL + 12, y + 28, n, r=12))
    svg.append(
        f'<rect x="{COL + 38}" y="{y + 6}" width="3" height="{slot - 24}" fill="{C["rossi"] if n in ROSSI_MOMENTS else C["grey"]}"/>'
    )
    svg.append(
        f'<foreignObject x="{COL + 52}" y="{y + 4}" width="{GUTTER_R - COL - 52}" height="{slot - 8}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="vcard"><b><i>LAP {m["lap"]}</i> {m["headline"]}</b>'
        f"<span>{m['story']}</span></div></foreignObject>"
    )
zone("E", COL - 10, top - 6, GUTTER_R - COL + 20, 7 * slot)

# ---- position strip, left to right ----------------------------------------------
x0, x1, axis_y, row = M + 64, 1030, 904, 16


def lx(lap: float) -> float:
    return x0 + lap * (x1 - x0) / 23


def ry(pos: float) -> float:
    return axis_y + 22 + (pos - 1) * row


svg.append(f'<text x="{M}" y="{axis_y - 26}" class="eyebrow">POSITIONS, LAP BY LAP</text>')
svg.append(
    f'<text x="{M + 196}" y="{axis_y - 26}" class="key">each line is a rider · higher = further ahead</text>'
)
svg.append(f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{C["muted"]}"/>')
for p_ in (1, 4, 8):
    svg.append(
        f'<text x="{x0 - 14}" y="{ry(p_) + 4:.1f}" class="axis" text-anchor="end">{ordinal(p_)}</text>'
    )
for lap in (0, 5, 10, 15, 20, 23):
    svg.append(
        f'<text x="{lx(lap):.1f}" y="{ry(8) + 26:.1f}" class="axis">{"Grid" if lap == 0 else f"Lap {lap}"}</text>'
    )
for m in moments:
    svg.append(
        f'<line x1="{lx(int(m["lap"])):.1f}" y1="{axis_y + 10}" x2="{lx(int(m["lap"])):.1f}" y2="{ry(8) + 8:.1f}" stroke="{C["rule"]}"/>'
    )


def hline(r: int) -> str:
    return " ".join(f"{lx(t / 10):.1f},{ry(position_at(POS[r], t / 10)):.1f}" for t in range(231))


for r in CONTEXT:
    svg.append(
        f'<polyline points="{hline(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>'
    )
svg.append(f'<polyline points="{hline(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>')
for m in moments:
    svg.append(badge(lx(int(m["lap"])), axis_y, int(m["moment_id"]), r=10))
for r, label in ((46, "Rossi · 1st"), (65, "Capirossi · 2nd")):
    y = ry(POS[r][-1])
    svg.append(
        f'<circle cx="{lx(23):.1f}" cy="{y:.1f}" r="5" fill="{C["rossi"] if r == 46 else C["capi"]}" stroke="{C["bg"]}" stroke-width="2"/>'
    )
    svg.append(f'<text x="{lx(23) + 12:.1f}" y="{y + 4:.1f}" class="endlabel">{label}</text>')
zone("F", M - 10, axis_y - 44, x1 - M + 140, ry(8) + 40 - axis_y + 44)

svg.append(
    f'<foreignObject x="{COL + 52}" y="{H - M + 12}" width="{GUTTER_R - COL - 52}" height="40"><div xmlns="http://www.w3.org/1999/xhtml" '
    f'class="creditbox">Data: official MotoGP timing (Tissot / Dorna) · Track: bacinger/f1-circuits (MIT) · '
    f"Story: MotoGP broadcast, Paddock Pass Podcast</div></foreignObject>"
)

note_svg = "".join(
    f'<g class="note"><rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="6" fill="none" '
    f'stroke="#4FD1C5" stroke-dasharray="6 5" stroke-width="1.2"/><circle cx="{x:.0f}" cy="{y:.0f}" r="11" '
    f'fill="#4FD1C5"/><text x="{x:.0f}" y="{y + 4.5:.0f}" class="tag">{tag}</text></g>'
    for tag, x, y, w, h in notes
)

NOTES = """
<h2>Layout D: refined</h2>
<p class="meta">100 × 70 cm landscape at 1.6 px/mm · real data, final colours, draft copy ·
images are placeholders · 55 mm margins.</p>
<ol class="zones">
<li><b>A · Title.</b> Title, subtitle and a one-sentence lede: the whole story for someone who
reads nothing else.</li>
<li><b>B · Images.</b> Helmet and 46 logo, top-right, above the story column.</li>
<li><b>C · Map (the hero).</b> TV orientation, about half the poster. <span class="y">Yellow
stretches</span> show where Rossi's moments happened. A small "how to read" key sits in the
empty bottom-left corner.</li>
<li><b>D · Key numbers.</b> In the map's empty top-right corner. Each figure carries the badge of
the moment it belongs to (0.575 s → ⑦, 0.002 s → ⑥).</li>
<li><b>E · Story.</b> The 7 moments as a list, read top to bottom. The cards have no boxes, just
a coloured bar (yellow = Rossi moment), for more air.</li>
<li><b>F · Positions strip.</b> Left to right, one plain-language hint ("higher = further
ahead"), badges on the lap axis, and only Rossi and Capirossi named.</li>
</ol>
<h3>Refinements over the first D sketch</h3>
<ul>
<li>Wider margins (55 mm) and card boxes removed, for more breathing room.</li>
<li>Map key added, so the badges and yellow stretches explain themselves.</li>
<li>Key numbers linked to their moments with badges.</li>
<li>A one-line reading hint on the positions strip.</li>
</ul>
<h3>Still open</h3>
<ul>
<li>Final title wording, and a dedication line for your dad?</li>
<li>Helmet photo: is it the 2006 Mugello special?</li>
<li>Paper: matte recommended for the dark background.</li>
</ul>
"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mugello 2006 Layout D</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;1,800&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#121110; color:{C["ink"]}; font:15px/1.5 Barlow, system-ui, sans-serif; }}
.wrap {{ display:flex; flex-wrap:wrap; gap:28px; padding:24px 16px; justify-content:center; }}
.poster {{ flex:1 1 960px; max-width:{W}px; min-width:0; }}
.poster svg {{ width:100%; height:auto; display:block; box-shadow:0 10px 40px #000a; }}
aside {{ flex:0 1 360px; background:#1E1C1B; border-radius:10px; padding:20px 22px; align-self:flex-start; }}
aside h2 {{ font:700 26px 'Barlow Condensed'; margin:0 0 4px; }}
aside h3 {{ font:600 18px 'Barlow Condensed'; margin:18px 0 4px; color:#4FD1C5; }}
.meta {{ color:{C["muted"]}; font-size:13px; }}
.zones li {{ margin-bottom:8px; }}
.y {{ background:{C["rossi"]}; color:{C["bg"]}; padding:0 4px; border-radius:3px; }}
.controls {{ display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-bottom:12px; font-size:14px; color:{C["muted"]}; }}
.controls button {{ font:inherit; color:{C["ink"]}; background:#1E1C1B; border:1px solid #3A3734; border-radius:6px; padding:4px 10px; cursor:pointer; }}
.controls button[aria-pressed="true"] {{ border-color:#4FD1C5; color:#4FD1C5; }}
.title {{ font:italic 800 104px 'Barlow Condensed'; fill:{C["ink"]}; }}
.subtitle {{ font:500 28px 'Barlow Condensed'; fill:{C["ink"]}; }}
.lede {{ font:400 18px/1.4 Barlow; color:{C["muted"]}; }}
.ph {{ font:500 12px Barlow; fill:{C["muted"]}; text-anchor:middle; }}
.corner {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; }}
.callout {{ font:600 15px 'Barlow Condensed'; fill:{C["ink"]}; }}
.badge {{ font-family:'Barlow Condensed'; font-weight:700; text-anchor:middle; }}
.eyebrow {{ font:600 13px 'Barlow Condensed'; fill:{C["muted"]}; letter-spacing:1.5px; }}
.key {{ font:400 13px Barlow; fill:{C["muted"]}; }}
.axis {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; text-anchor:middle; }}
.endlabel {{ font:600 13px 'Barlow Condensed'; fill:{C["ink"]}; }}
.vcard {{ font:400 13px/1.35 Barlow; color:{C["ink"]}; }}
.vcard b {{ display:block; font:600 17px/1.2 'Barlow Condensed'; margin-bottom:3px; }}
.vcard i {{ font-style:normal; color:{C["muted"]}; letter-spacing:1px; margin-right:6px; font-size:13px; }}
.stat {{ font:600 46px Barlow; fill:{C["ink"]}; }}
.statlabel {{ font:400 14px Barlow; fill:{C["muted"]}; }}
.creditbox {{ font:400 10px/1.4 Barlow; color:{C["muted"]}; }}
.tag {{ font:700 12px Barlow; fill:#0B2B28; text-anchor:middle; }}
.hide-notes .note {{ display:none; }}
</style></head><body>
<div class="wrap">
  <div class="poster">
    <div class="controls" role="group" aria-label="Preview mode">
      <span>Preview as:</span>
      <button data-f="none" aria-pressed="true">Normal vision</button>
      <button data-f="url(#protan)" aria-pressed="false">Protanopia</button>
      <button data-f="url(#deutan)" aria-pressed="false">Deuteranopia</button>
      <button data-f="grayscale(1)" aria-pressed="false">Greyscale print</button>
      <label><input type="checkbox" id="notes"> Zone outlines</label>
    </div>
    <svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d" class="hide-notes">
      <title id="t">Mugello 2006 poster, layout D</title>
      <desc id="d">Wide poster: Mugello map with Rossi's key moments painted yellow and numbered, a column of seven story cards, and a strip showing positions lap by lap.</desc>
      <defs>
        <filter id="protan"><feColorMatrix type="matrix" values="0.152 1.053 -0.205 0 0  0.115 0.786 0.099 0 0  -0.004 -0.048 1.052 0 0  0 0 0 1 0"/></filter>
        <filter id="deutan"><feColorMatrix type="matrix" values="0.367 0.861 -0.228 0 0  0.280 0.673 0.047 0 0  -0.012 0.043 0.969 0 0  0 0 0 1 0"/></filter>
      </defs>
      <g id="art">{"".join(svg)}{note_svg}</g>
    </svg>
  </div>
  <aside>{NOTES}</aside>
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
