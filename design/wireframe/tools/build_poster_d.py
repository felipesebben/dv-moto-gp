"""Refined wireframe for layout D (120 x 70 cm landscape).

Run: uv run python design/wireframe/tools/build_poster_d.py
Writes design/wireframe/poster_d.html. Sketch tool only: the real poster is built in Tableau.
Event facts below are copied from the official classification PDF and the track GeoJSON;
the build will read them from the pipeline instead.
"""

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from sketchlib import (  # noqa: E402
    C, CONTEXT, POS, ROSSI_MOMENTS, badge, fit, load, ordinal, path, position_at,
)

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "design" / "wireframe" / "poster_d.html"
track, corners, moments = load(ROOT)

PX = 1.6  # px per mm
W, H = round(1200 * PX), round(700 * PX)
M = 88  # 55 mm margin
COL = 1420  # story column
RIGHT = W - M
ITALY = {"green": "#229457", "white": C["ink"], "red": "#CE2B37"}  # flag red, kept apart from Capirossi's coral

# ---- map placement ------------------------------------------------------------
MAP = (M, 300, 1240, 516)  # x, y, w, h (height-bound, centred)
pts = fit(track, *MAP)
SCALE = MAP[3] / 705
CALLOUT = {0: (-136, -204, -20, 5, "end"), 1: (-14, 141, -12, 32, "start"),
           8: (-8, -125, -12, 32, "start"), 9: (-54, 35, -20, 5, "end")}
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end")}
STRETCHES = [range(7, 14), range(57, 65), [*range(125, 129), 0]]

svg: list[str] = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']

# ---- header: title (+ Italian accent variants), subtitle, lede, commentary quote ---
TITLE_X, TITLE_Y, TITLE_W = M - 4, 160, 530
svg.append(f'<text x="{TITLE_X}" y="{TITLE_Y}" class="title">MUGELLO 2006</text>')
# variant 1: a thin tricolore rule under the title
seg = TITLE_W / 3
svg.append('<g class="acc acc-rule">' + "".join(
    f'<rect x="{M + i * seg:.1f}" y="{TITLE_Y + 12}" width="{seg - 3:.1f}" height="4" fill="{c}"/>'
    for i, c in enumerate(ITALY.values())
) + "</g>")
# variant 2: a slanted livery flash after the title, matching the italic
fx = M + TITLE_W + 26
svg.append('<g class="acc acc-flash">' + "".join(
    f'<polygon points="{fx + i * 16 + 18},{TITLE_Y - 74} {fx + i * 16 + 28},{TITLE_Y - 74} '
    f'{fx + i * 16 + 10},{TITLE_Y} {fx + i * 16},{TITLE_Y}" fill="{c}"/>'
    for i, c in enumerate(ITALY.values())
) + "</g>")
# variant 3: tricolore only on the year
svg.append(f'<g class="acc acc-year"><defs><linearGradient id="tri" gradientUnits="userSpaceOnUse" x1="{TITLE_X + 358}" x2="{TITLE_X + 536}">'
           f'<stop offset="0.333" stop-color="{ITALY["green"]}"/><stop offset="0.333" stop-color="{ITALY["white"]}"/>'
           f'<stop offset="0.666" stop-color="{ITALY["white"]}"/><stop offset="0.666" stop-color="{ITALY["red"]}"/>'
           f'</linearGradient></defs><text x="{TITLE_X}" y="{TITLE_Y}" class="title" fill-opacity="0">MUGELLO '
           f'<tspan fill="url(#tri)" fill-opacity="1">2006</tspan></text></g>')
svg.append(f'<text x="{M}" y="212" class="subtitle">Gran Premio d&#8217;Italia Alice · Rossi vs Capirossi · Sunday 4 June 2006</text>')
svg.append(
    f'<foreignObject x="{M}" y="224" width="760" height="60"><div xmlns="http://www.w3.org/1999/xhtml" class="lede">'
    f"Behind in the championship and in front of his home crowd, Valentino Rossi falls from first "
    f"to fifth with eight laps to go, then wins by half a second.</div></foreignObject>"
)
svg.append(
    f'<foreignObject x="900" y="84" width="440" height="190" class="quote-wrap"><div xmlns="http://www.w3.org/1999/xhtml" class="quote">'
    f"<q>He&#8217;s done it! Valentino Rossi has won the Italian Grand Prix here at Mugello. "
    f"What a victory for the Doctor!</q><span>TV commentary, as Rossi crosses the line</span></div></foreignObject>"
)

# ---- images: the Mugello 2006 helmet leads the column ------------------------------
svg.append(f'<rect x="{COL}" y="{M}" width="232" height="172" rx="8" fill="none" stroke="{C["muted"]}" stroke-dasharray="4 4"/>')
svg.append(f'<text x="{COL + 116}" y="{M + 90}" class="ph">IMAGE · helmet</text>')
svg.append(f'<text x="{COL}" y="{M + 192}" class="caption">Rossi&#8217;s helmet for Mugello 2006</text>')
svg.append(f'<rect x="{COL + 252}" y="{M}" width="{RIGHT - COL - 252}" height="172" rx="8" fill="none" stroke="{C["muted"]}" stroke-dasharray="4 4"/>')
svg.append(f'<text x="{(COL + 252 + RIGHT) / 2}" y="{M + 90}" class="ph">IMAGE · 46 logo</text>')

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

# circuit card, quiet, in the empty bottom-left of the map area
# (circuit information + classification PDFs; name and town from the track GeoJSON)
card_x, card_y = M, 640
svg.append(f'<text x="{card_x}" y="{card_y}" class="eyebrow">THE CIRCUIT</text>')
svg.append(f'<text x="{card_x}" y="{card_y + 24}" class="circuit">Autodromo Internazionale del Mugello</text>')
for i, line in enumerate([
    "Scarperia e San Piero, Tuscany · built 1974",
    "5,245 m long · 14 m wide · clockwise",
    "15 corners: 9 right, 6 left",
    "Longest straight 1,141 m",
    "Race: 23 laps · 120.6 km · dry, air 20 °C, track 29 °C",
]):
    svg.append(f'<text x="{card_x}" y="{card_y + 46 + i * 19}" class="meta">{line}</text>')

# key numbers, right of the circuit, each tied to its moment
STATS = [("0.575 s", "Rossi&#8217;s winning margin", 7), ("0.002 s", "between them after lap 22", 6), ("5", "Mugello wins in a row", None)]
for i, (v, label, n) in enumerate(STATS):
    y = 360 + i * 74
    svg.append(f'<text x="1130" y="{y}" class="stat">{v}</text>')
    svg.append(f'<text x="1132" y="{y + 22}" class="statlabel">{label}</text>')
    if n:
        svg.append(badge(1112, y - 16, n, r=9))

# ---- story column ---------------------------------------------------------------
top, slot = 300, 104
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
x0, x1, axis_y, row = M + 64, 1300, 900, 16


def lx(lap: float) -> float:
    return x0 + lap * (x1 - x0) / 23


def ry(pos: float) -> float:
    return axis_y + 22 + (pos - 1) * row


svg.append(f'<text x="{M}" y="{axis_y - 26}" class="eyebrow">POSITIONS, LAP BY LAP <tspan class="hint">· higher = further ahead</tspan></text>')
svg.append(f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{C["muted"]}"/>')
for p_ in (1, 4, 8):
    svg.append(f'<text x="{x0 - 14}" y="{ry(p_) + 4:.1f}" class="axis" text-anchor="end">{ordinal(p_)}</text>')
for lap in (0, 5, 10, 15, 20, 23):
    svg.append(f'<text x="{lx(lap):.1f}" y="{ry(8) + 26:.1f}" class="axis">{"Grid" if lap == 0 else f"Lap {lap}"}</text>')
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
fy = H - 40
svg.append(badge(M + 7, fy - 4, 4, r=7))
svg.append(f'<text x="{M + 20}" y="{fy}" class="foot">Rossi moment</text>')
svg.append(badge(M + 118, fy - 4, 2, r=7))
svg.append(f'<text x="{M + 131}" y="{fy}" class="foot">other moment</text>')
svg.append(f'<line x1="{M + 232}" y1="{fy - 4}" x2="{M + 248}" y2="{fy - 4}" stroke="{C["rossi"]}" stroke-width="6" stroke-linecap="round"/>')
svg.append(f'<text x="{M + 256}" y="{fy}" class="foot">where it happened · numbers match the stories</text>')
svg.append(
    f'<text x="{RIGHT}" y="{fy}" class="foot" text-anchor="end">Data: official MotoGP timing (Tissot / Dorna) · '
    f"Track: bacinger/f1-circuits (MIT) · Story: MotoGP broadcast, Paddock Pass Podcast</text>"
)

NOTES = """
<h2>Layout D, round 3</h2>
<p class="meta">120 × 70 cm landscape (wider) at 1.6 px/mm · real data and event facts ·
images are placeholders.</p>
<h3>What changed</h3>
<ul>
<li><b>Wider:</b> 120 × 70 cm. The map keeps its height, and the extra width gives the key numbers
their own space to the right of the track and lets the story column breathe.</li>
<li><b>Quieter legends:</b> the map key is one small line in the footer. The positions hint shares
the strip's title line.</li>
<li><b>Emotion:</b> the TV call at the finish as a quote in the header, "in front of his home
crowd" in the lede, and the helmet captioned as the Mugello 2006 design.</li>
<li><b>Mugello facts</b> (from the classification PDF): the event's official name
<i>Gran Premio d&#8217;Italia <b>Alice</b></i> in the subtitle, and a quiet circuit card
bottom-left: full circuit name, town, year built, length, width, corners (9 right, 6 left), longest straight, and the race distance and conditions (from the circuit information and classification PDFs).</li>
</ul>
<h3>Test: Italian accent on the title</h3>
<p>Use the "Title accent" buttons above the poster. The flag red is <code>#CE2B37</code>, kept apart
from Capirossi's coral so it doesn't read as "his" colour.</p>
<h3>Test: quote</h3>
<p>Toggle it off to compare how loud the header feels without it.</p>
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
.title {{ font:italic 800 104px 'Barlow Condensed'; fill:{C["ink"]}; }}
.subtitle {{ font:500 26px 'Barlow Condensed'; fill:{C["ink"]}; }}
.lede {{ font:400 18px/1.4 Barlow; color:{C["muted"]}; }}
.quote {{ font:italic 600 25px/1.2 'Barlow Condensed'; color:{C["ink"]}; border-left:3px solid {C["rossi"]}; padding-left:16px; }}
.quote q {{ quotes:"\\201C" "\\201D"; display:block; }}
.quote span {{ display:block; margin-top:8px; font:400 13px Barlow; color:{C["muted"]}; }}
.ph {{ font:500 12px Barlow; fill:{C["muted"]}; text-anchor:middle; }}
.caption {{ font:italic 400 13px Barlow; fill:{C["muted"]}; }}
.corner {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; }}
.callout {{ font:600 15px 'Barlow Condensed'; fill:{C["ink"]}; }}
.badge {{ font-family:'Barlow Condensed'; font-weight:700; text-anchor:middle; }}
.eyebrow {{ font:600 13px 'Barlow Condensed'; fill:{C["muted"]}; letter-spacing:1.5px; }}
.hint {{ font:400 13px Barlow; letter-spacing:0; }}
.circuit {{ font:600 17px 'Barlow Condensed'; fill:{C["ink"]}; }}
.meta {{ font:400 13px Barlow; fill:{C["muted"]}; }}
.axis {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; text-anchor:middle; }}
.endlabel {{ font:600 13px 'Barlow Condensed'; fill:{C["ink"]}; }}
.vcard {{ font:400 13px/1.35 Barlow; color:{C["ink"]}; }}
.vcard b {{ display:block; font:600 17px/1.2 'Barlow Condensed'; margin-bottom:3px; }}
.vcard i {{ font-style:normal; color:{C["muted"]}; letter-spacing:1px; margin-right:6px; font-size:13px; }}
.stat {{ font:600 46px Barlow; fill:{C["ink"]}; }}
.statlabel {{ font:400 14px Barlow; fill:{C["muted"]}; }}
.foot {{ font:400 11px Barlow; fill:{C["muted"]}; }}
.acc {{ display:none; }}
svg[data-accent="rule"] .acc-rule, svg[data-accent="flash"] .acc-flash, svg[data-accent="year"] .acc-year {{ display:inline; }}
svg[data-quote="off"] .quote-wrap {{ display:none; }}
</style></head><body><main>
<div class="poster">
  <div class="controls">
    <div class="grp" data-attr="accent" role="group" aria-label="Title accent"><span>Title accent:</span>
      <button data-v="none" aria-pressed="true">None</button>
      <button data-v="rule" aria-pressed="false">Tricolore rule</button>
      <button data-v="flash" aria-pressed="false">Livery flash</button>
      <button data-v="year" aria-pressed="false">Tricolore year</button></div>
    <div class="grp" data-attr="quote" role="group" aria-label="Quote"><span>Quote:</span>
      <button data-v="on" aria-pressed="true">On</button>
      <button data-v="off" aria-pressed="false">Off</button></div>
    <div class="grp" data-attr="filter" role="group" aria-label="Preview"><span>Preview:</span>
      <button data-v="none" aria-pressed="true">Normal</button>
      <button data-v="url(#protan)" aria-pressed="false">Protanopia</button>
      <button data-v="url(#deutan)" aria-pressed="false">Deuteranopia</button>
      <button data-v="grayscale(1)" aria-pressed="false">Greyscale</button></div>
  </div>
  <svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d" data-accent="none" data-quote="on">
    <title id="t">Mugello 2006 poster, layout D</title>
    <desc id="d">Wide poster: Mugello map with Rossi's key moments painted yellow and numbered, the TV call at the finish, circuit facts, a column of seven story cards and a strip of positions lap by lap.</desc>
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
document.querySelectorAll('.controls .grp').forEach(g => g.querySelectorAll('button').forEach(b => b.addEventListener('click', () => {{
  g.querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', x === b));
  if (g.dataset.attr === 'filter') art.style.filter = b.dataset.v;
  else svg.dataset[g.dataset.attr] = b.dataset.v;
}})));
</script>
</body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
