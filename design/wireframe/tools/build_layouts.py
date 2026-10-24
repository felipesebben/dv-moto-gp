"""Layout options B (vertical race column) and C (ring around the circuit) - scratch sketch tool."""

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
    envelope,
    fit,
    load,
    ordinal,
    outward_normals,
    path,
    position_at,
)

ROOT = Path(sys.argv[1])
OUT = ROOT / "design" / "wireframe" / "layout_options.html"
track, corners, moments = load(ROOT)
W, H, M = 1600, 1120, 72  # landscape 100 x 70 cm at 1.6 px/mm

# callouts: badge offset in track units (1000-wide track), text offset in px, anchor
CALLOUT = {
    0: (-136, -204, -20, 5, "end"),
    1: (-14, 141, -12, 32, "start"),
    8: (-8, -125, -12, 32, "start"),
    9: (-54, 35, -20, 5, "end"),
}
LABEL_FIX = {2: (0, 24, "middle"), 4: (0, 26, "middle"), 9: (12, 18, "start"), 10: (-12, 16, "end")}


def header(svg: list[str]) -> None:
    svg.append(f'<text x="{M}" y="150" class="title">MUGELLO 2006</text>')
    svg.append(
        f'<text x="{M + 3}" y="196" class="subtitle">Rossi vs Capirossi · Gran Premio d\'Italia · 4 June 2006</text>'
    )
    svg.append(
        f'<foreignObject x="{M + 3}" y="212" width="760" height="60"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'class="lede">Behind in the championship, Valentino Rossi falls from first to fifth with eight '
        f"laps to go, then wins by half a second.</div></foreignObject>"
    )
    for i, label in enumerate(["46 logo", "helmet"]):
        x = W - M - 150 - i * 166
        svg.append(
            f'<rect x="{x}" y="88" width="150" height="150" rx="8" fill="none" stroke="{C["muted"]}" stroke-dasharray="4 4"/>'
        )
        svg.append(f'<text x="{x + 75}" y="168" class="ph">IMAGE · {label}</text>')


def footer(svg: list[str], y: float) -> None:
    stats = [
        ("0.575 s", "Rossi's winning margin"),
        ("0.002 s", "between them after lap 22"),
        ("5", "Mugello wins in a row"),
    ]
    for i, (v, label) in enumerate(stats):
        x = M + i * 330
        svg.append(
            f'<text x="{x}" y="{y}" class="stat">{v}</text><text x="{x + 2}" y="{y + 26}" class="statlabel">{label}</text>'
        )
    svg.append(
        f'<text x="{W - M}" y="{y + 26}" class="credit" text-anchor="end">Data: official MotoGP timing (Tissot / Dorna) · '
        f"Track: bacinger/f1-circuits (MIT) · Story: MotoGP broadcast, Paddock Pass Podcast</text>"
    )


def draw_map(
    svg: list[str],
    pts: list[tuple[float, float]],
    scale: float,
    callouts: bool,
    inward: bool = False,
    highlight: bool = False,
) -> None:
    svg.append(
        f'<path d="{path(pts, True)}" fill="none" stroke="{C["ink"]}" stroke-width="7" stroke-linejoin="round"/>'
    )
    if (
        highlight
    ):  # where Rossi's moments happened: braking into San Donato, Arrabbiata 1, the run to the line
        for seg in (range(7, 14), range(57, 65), list(range(125, 129)) + [0]):
            seg_pts = [pts[i] for i in seg]
            svg.append(
                f'<path d="{path(seg_pts)}" fill="none" stroke="{C["rossi"]}" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>'
            )
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    sx, sy = pts[0]
    svg.append(f'<rect x="{sx - 3}" y="{sy - 14}" width="6" height="28" fill="{C["green"]}"/>')
    svg.append(f'<text x="{sx + 10:.1f}" y="{sy - 12:.1f}" class="corner">Start / Finish</text>')
    for turn, (name, idx) in corners.items():
        if turn == 0:
            continue
        x, y = pts[idx]
        vx, vy = x - cx, y - cy
        n = math.hypot(vx, vy) or 1
        lx, ly, anchor = x + vx / n * 16, y + vy / n * 16 + 4, "start" if vx > 0 else "end"
        if inward:
            lx, ly, anchor = x - vx / n * 14, y - vy / n * 14 + 4, "end" if vx > 0 else "start"
        elif turn in LABEL_FIX:
            dx, dy, anchor = LABEL_FIX[turn]
            lx, ly = x + dx, y + dy
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{C["muted"]}"/>')
        if not inward:
            svg.append(
                f'<text x="{lx:.1f}" y="{ly:.1f}" class="corner" text-anchor="{anchor}">{name}</text>'
            )
    by_turn: dict[int, list[dict[str, str]]] = {}
    for m in moments:
        if m["turn"]:
            by_turn.setdefault(int(m["turn"]), []).append(m)
    for turn, ms in by_turn.items():
        x, y = pts[corners[turn][1]]
        if callouts:
            ux, uy, tdx, tdy, anchor = CALLOUT[turn]
            bx, by = x + ux * scale, y + uy * scale
        else:  # badges hug the corner, no text
            vx, vy = x - cx, y - cy
            n = math.hypot(vx, vy) or 1
            bx, by = x - vx / n * 26, y - vy / n * 26
        for j, m in enumerate(ms):
            svg.append(
                f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{bx + j * 30:.1f}" y2="{by:.1f}" stroke="{C["muted"]}" stroke-width="1"/>'
            )
            svg.append(badge(bx + j * 30, by, int(m["moment_id"])))
        if callouts:
            for j, m in enumerate(ms):
                svg.append(
                    f'<text x="{bx + tdx:.1f}" y="{by + tdy + j * 18:.1f}" class="callout" text-anchor="{anchor}">{m["moment_id"]} · {m["headline"]}</text>'
                )


def card(svg: list[str], x: float, y: float, w: float, h: float, m: dict[str, str]) -> None:
    n = int(m["moment_id"])
    svg.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{C["card"]}"/>'
    )
    svg.append(
        f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="{h:.1f}" fill="{C["rossi"] if n in ROSSI_MOMENTS else C["grey"]}"/>'
    )
    svg.append(
        f'<foreignObject x="{x + 14:.1f}" y="{y + 8:.1f}" width="{w - 24:.1f}" height="{h - 12:.1f}">'
        f'<div xmlns="http://www.w3.org/1999/xhtml" class="vcard"><b><i>LAP {m["lap"]}</i> {m["headline"]}</b>'
        f"<span>{m['story']}</span></div></foreignObject>"
    )


# ---------------------------------------------------------------- B: vertical race column
def layout_b() -> str:
    svg = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
    header(svg)
    pts = fit(track, M + 10, 300, 880, 690)
    draw_map(svg, pts, 880 / 1000, callouts=True)

    top, bottom = 352, 984

    def ly(lap: float) -> float:
        return top + lap * (bottom - top) / 23

    c0, cw = 1036, 19

    def px(pos: float) -> float:
        return c0 + (pos - 1) * cw

    svg.append(f'<text x="{c0 - 8}" y="300" class="eyebrow">THE RACE, LAP BY LAP</text>')
    for p in range(1, 9):
        svg.append(f'<text x="{px(p):.1f}" y="330" class="axis">{p}</text>')
    svg.append(f'<text x="{px(1) - 14:.1f}" y="330" class="axis" text-anchor="end">pos.</text>')
    for lap in range(24):
        if lap in (0, 5, 10, 15, 20, 23):
            svg.append(
                f'<text x="{c0 - 22}" y="{ly(lap) + 4:.1f}" class="axis" text-anchor="end">{"Grid" if lap == 0 else f"Lap {lap}"}</text>'
            )
    for m in moments:
        y = ly(int(m["lap"]))
        svg.append(
            f'<line x1="{px(1) - 8:.1f}" y1="{y:.1f}" x2="{px(8) + 18:.1f}" y2="{y:.1f}" stroke="{C["rule"]}"/>'
        )

    def vline(r: int) -> str:
        return " ".join(
            f"{px(position_at(POS[r], t / 10)):.1f},{ly(t / 10):.1f}" for t in range(231)
        )

    for r in CONTEXT:
        svg.append(
            f'<polyline points="{vline(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>'
        )
    svg.append(
        f'<polyline points="{vline(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>'
    )
    svg.append(f'<polyline points="{vline(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
    svg.append(
        f'<polyline points="{vline(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>'
    )
    for r, label, col in ((46, "Rossi", C["rossi"]), (65, "Capirossi", C["capi"])):
        x = px(POS[r][-1])
        svg.append(
            f'<circle cx="{x:.1f}" cy="{ly(23):.1f}" r="5" fill="{col}" stroke="{C["bg"]}" stroke-width="2"/>'
        )
        side = -1 if r == 46 else 1
        svg.append(
            f'<text x="{x + side * 10:.1f}" y="{ly(23) + 20:.1f}" class="endlabel" text-anchor="{"end" if side < 0 else "start"}">{label} · {ordinal(POS[r][-1])}</text>'
        )
    # cards spread evenly, linked to their lap
    bx, x0 = 1206, 1236
    slot = 104
    for i, m in enumerate(moments):
        y = ly(int(m["lap"]))
        cy = 300 + i * slot
        svg.append(
            f'<path d="M{px(8) + 18:.1f},{y:.1f} L{bx:.1f},{y:.1f} C{bx + 16:.1f},{y:.1f} {x0 - 16:.1f},{cy + slot / 2 - 3:.1f} {x0:.1f},{cy + slot / 2 - 3:.1f}" fill="none" stroke="{C["muted"]}" stroke-width="1"/>'
        )
        svg.append(badge(bx, y, int(m["moment_id"]), r=11))
        card(svg, x0, cy, W - M - x0, slot - 6, m)
    footer(svg, 1064)
    return "".join(svg)


# ---------------------------------------------------------------- C: ring around the circuit
def layout_c() -> str:
    svg = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
    header(svg)
    pts = fit(track, M + 160, 430, 700, 450)
    N, BASE, GAP = 720, 34, 8
    ring = envelope(pts, N, 12)
    normals = outward_normals(ring)
    START, END = 0.015, 0.985

    def at(lap_f: float, off: float) -> tuple[float, float]:
        j = int((START + lap_f / 23 * (END - START)) * N) % N
        (gx, gy), (nx, ny) = ring[j], normals[j]
        return gx + nx * off, gy + ny * off

    def lane(r: int) -> str:
        return path(
            [at(t / 20, BASE + (position_at(POS[r], t / 20) - 1) * GAP) for t in range(461)]
        )

    for r in CONTEXT:
        svg.append(f'<path d="{lane(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>')
    svg.append(f'<path d="{lane(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>')
    svg.append(f'<path d="{lane(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
    svg.append(f'<path d="{lane(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>')
    outer = BASE + 7 * GAP
    for lap in (0, 5, 10, 15, 20, 23):
        x, y = at(lap, outer + 52)
        svg.append(
            f'<text x="{x:.1f}" y="{y + 4:.1f}" class="axis">{"Start" if lap == 0 else "Finish" if lap == 23 else f"Lap {lap}"}</text>'
        )
    for m in moments:
        lap = int(m["lap"])
        x0_, y0_ = at(lap, BASE - 10)
        x1_, y1_ = at(lap, outer + 4)
        svg.append(
            f'<line x1="{x0_:.1f}" y1="{y0_:.1f}" x2="{x1_:.1f}" y2="{y1_:.1f}" stroke="{C["muted"]}" stroke-width="1"/>'
        )
        bx, by = at(lap, outer + 16 + (22 if lap == 22 else 0))
        svg.append(badge(bx, by, int(m["moment_id"]), r=9))
    sx, sy = pts[0]
    rx, ry = at(0, BASE)
    svg.append(
        f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{rx:.1f}" y2="{ry:.1f}" stroke="{C["green"]}" stroke-width="1.5" stroke-dasharray="3 4"/>'
    )
    draw_map(svg, pts, 700 / 1000, callouts=False, inward=True)
    svg.append(
        f'<foreignObject x="{M}" y="300" width="420" height="80"><div xmlns="http://www.w3.org/1999/xhtml" class="howto">'
        f"<b>How to read the ring:</b> the whole race runs once around the circuit, clockwise from the start line. "
        f"Each line is a rider; the closer to the track, the higher the position.</div></foreignObject>"
    )
    # vertical story column
    x0, top = 1060, 300
    slot = 104
    svg.append(
        f'<line x1="{x0 + 12}" y1="{top + 14}" x2="{x0 + 12}" y2="{top + 6 * slot + 60}" stroke="{C["rule"]}" stroke-width="2"/>'
    )
    for i, m in enumerate(moments):
        y = top + i * slot
        svg.append(badge(x0 + 12, y + 30, int(m["moment_id"]), r=12))
        card(svg, x0 + 36, y, W - M - x0 - 36, slot - 10, m)
    footer(svg, 1064)
    return "".join(svg)


# ---------------------------------------------------------------- D: hybrid (wide, map-led)
def layout_d() -> str:
    svg = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
    # title block (left), images (right column top)
    svg.append(f'<text x="{M}" y="150" class="title">MUGELLO 2006</text>')
    svg.append(
        f'<text x="{M + 3}" y="194" class="subtitle">Rossi vs Capirossi · Gran Premio d&#8217;Italia · 4 June 2006</text>'
    )
    svg.append(
        f'<foreignObject x="{M + 3}" y="208" width="720" height="60"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'class="lede">Behind in the championship, Valentino Rossi falls from first to fifth with eight '
        f"laps to go, then wins by half a second.</div></foreignObject>"
    )
    col = 1136
    for i, label in enumerate(["helmet", "46 logo"]):
        x = col + i * 204
        svg.append(
            f'<rect x="{x}" y="72" width="188" height="150" rx="8" fill="none" stroke="{C["muted"]}" stroke-dasharray="4 4"/>'
        )
        svg.append(f'<text x="{x + 94}" y="152" class="ph">IMAGE · {label}</text>')
    # the map, dominant
    pts = fit(track, M, 300, 1010, 530)
    draw_map(svg, pts, 530 / 705, callouts=True, highlight=True)
    # key numbers in the empty top-right corner of the map area
    for i, (v, label) in enumerate(
        [
            ("0.575 s", "Rossi's winning margin"),
            ("0.002 s", "between them after lap 22"),
            ("5", "Mugello wins in a row"),
        ]
    ):
        y = 352 + i * 70
        svg.append(
            f'<text x="{880}" y="{y}" class="stat">{v}</text><text x="{882}" y="{y + 22}" class="statlabel">{label}</text>'
        )
    # story column (right), in race order
    top, slot = 250, 108
    svg.append(
        f'<line x1="{col + 12}" y1="{top + 30}" x2="{col + 12}" y2="{top + 6 * slot + 30}" stroke="{C["rule"]}" stroke-width="2"/>'
    )
    for i, m in enumerate(moments):
        y = top + i * slot
        svg.append(badge(col + 12, y + 30, int(m["moment_id"]), r=12))
        card(svg, col + 36, y, W - M - col - 36, slot - 10, m)
    # compact position strip under the map, left to right
    x0, x1, axis_y, row = M + 70, 1010, 930, 15

    def lx(lap: float) -> float:
        return x0 + lap * (x1 - x0) / 23

    def ry(pos: float) -> float:
        return axis_y + 22 + (pos - 1) * row

    svg.append(f'<text x="{M}" y="{axis_y - 22}" class="eyebrow">POSITIONS, LAP BY LAP</text>')
    svg.append(f'<line x1="{x0}" y1="{axis_y}" x2="{x1}" y2="{axis_y}" stroke="{C["muted"]}"/>')
    for lap in (0, 5, 10, 15, 20, 23):
        svg.append(
            f'<text x="{lx(lap):.1f}" y="{ry(8) + 24:.1f}" class="axis">{"Grid" if lap == 0 else f"Lap {lap}"}</text>'
        )
    for p_ in (1, 4, 8):
        svg.append(
            f'<text x="{x0 - 12}" y="{ry(p_) + 4:.1f}" class="axis" text-anchor="end">{ordinal(p_)}</text>'
        )
    for m in moments:
        lap = int(m["lap"])
        svg.append(
            f'<line x1="{lx(lap):.1f}" y1="{axis_y + 10}" x2="{lx(lap):.1f}" y2="{ry(8) + 6:.1f}" stroke="{C["rule"]}"/>'
        )

    def hline(r: int) -> str:
        return " ".join(
            f"{lx(t / 10):.1f},{ry(position_at(POS[r], t / 10)):.1f}" for t in range(231)
        )

    for r in CONTEXT:
        svg.append(
            f'<polyline points="{hline(r)}" fill="none" stroke="{C["grey"]}" stroke-width="1.5"/>'
        )
    svg.append(
        f'<polyline points="{hline(65)}" fill="none" stroke="{C["capi"]}" stroke-width="3"/>'
    )
    svg.append(f'<polyline points="{hline(46)}" fill="none" stroke="{C["bg"]}" stroke-width="7"/>')
    svg.append(
        f'<polyline points="{hline(46)}" fill="none" stroke="{C["rossi"]}" stroke-width="4"/>'
    )
    for m in moments:
        svg.append(badge(lx(int(m["lap"])), axis_y, int(m["moment_id"]), r=10))
    for r, label in ((46, "Rossi · 1st"), (65, "Capirossi · 2nd")):
        y = ry(POS[r][-1])
        svg.append(
            f'<circle cx="{lx(23):.1f}" cy="{y:.1f}" r="5" fill="{C["rossi"] if r == 46 else C["capi"]}" stroke="{C["bg"]}" stroke-width="2"/>'
        )
        svg.append(f'<text x="{lx(23) + 12:.1f}" y="{y + 4:.1f}" class="endlabel">{label}</text>')
    svg.append(
        f'<foreignObject x="{col + 36}" y="{H - 66}" width="{W - M - col - 36}" height="40"><div xmlns="http://www.w3.org/1999/xhtml" '
        f'class="creditbox">Data: official MotoGP timing (Tissot / Dorna) · Track: bacinger/f1-circuits (MIT) · '
        f"Story: MotoGP broadcast, Paddock Pass Podcast</div></foreignObject>"
    )
    return "".join(svg)


STYLE = f"""
* {{ box-sizing:border-box; }}
body {{ margin:0; background:#121110; color:{C["ink"]}; font:15px/1.5 Barlow, system-ui, sans-serif; }}
main {{ max-width:1640px; margin:0 auto; padding:24px 16px 64px; }}
h1 {{ font:700 32px 'Barlow Condensed'; margin:0 0 4px; }}
h2 {{ font:700 26px 'Barlow Condensed'; margin:40px 0 8px; }}
.intro, .pros {{ color:{C["muted"]}; max-width:1100px; }}
.pros b {{ color:{C["ink"]}; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:12px 32px; max-width:1100px; }}
svg {{ width:100%; height:auto; display:block; margin-top:12px; box-shadow:0 10px 40px #000a; }}
.title {{ font:italic 800 96px 'Barlow Condensed'; fill:{C["ink"]}; }}
.subtitle {{ font:500 28px 'Barlow Condensed'; fill:{C["ink"]}; }}
.lede {{ font:400 18px/1.4 Barlow; color:{C["muted"]}; }}
.howto {{ font:400 13px/1.4 Barlow; color:{C["muted"]}; }} .howto b {{ color:{C["ink"]}; font-weight:600; }}
.ph {{ font:500 12px Barlow; fill:{C["muted"]}; text-anchor:middle; }}
.corner {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; }}
.callout {{ font:600 15px 'Barlow Condensed'; fill:{C["ink"]}; }}
.badge {{ font-family:'Barlow Condensed'; font-weight:700; text-anchor:middle; }}
.eyebrow {{ font:600 13px 'Barlow Condensed'; fill:{C["muted"]}; letter-spacing:1.5px; }}
.axis {{ font:500 12px 'Barlow Condensed'; fill:{C["muted"]}; text-anchor:middle; }}
.endlabel {{ font:600 13px 'Barlow Condensed'; fill:{C["ink"]}; }}
.vcard {{ font:400 12.5px/1.3 Barlow; color:{C["ink"]}; }}
.vcard b {{ display:block; font:600 16px/1.2 'Barlow Condensed'; margin-bottom:3px; }}
.vcard i {{ font-style:normal; color:{C["muted"]}; letter-spacing:1px; margin-right:6px; font-size:13px; }}
.stat {{ font:600 46px Barlow; fill:{C["ink"]}; }}
.statlabel {{ font:400 14px Barlow; fill:{C["muted"]}; }}
.credit {{ font:400 10px Barlow; fill:{C["muted"]}; }}
.creditbox {{ font:400 10px/1.4 Barlow; color:{C["muted"]}; }}
"""

html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Mugello 2006 Layouts</title>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,500;0,600;0,700;1,800&family=Barlow:wght@400;500;600&display=swap" rel="stylesheet">
<style>{STYLE}</style></head><body><main>
<h1>Mugello 2006: layout options</h1>
<p class="intro">Same data, palette, fonts and story text as the portrait wireframe
(<a href="poster_wireframe.html" style="color:{C["ink"]}">option A</a>). Both options here are
landscape 100 × 70 cm, which gives the map more room and more air. Map in TV orientation.</p>

<h2>Option D (recommended): wide, map-led hybrid</h2>
<div class="grid pros">
<p><b>How it reads:</b> title → the big map (the stretches where Rossi's moments happened are painted
yellow) → the 7 story cards on the right, read top to bottom like a list → the compact position
strip under the map, read left to right like A. The key numbers sit in the map's empty corner.</p>
<p><b>Takes from each:</b> B's landscape and card column, A's familiar left-to-right chart (now
compact), C's idea of putting the story <i>on</i> the circuit, without inventing data.
<b>Yellow stretches:</b> braking into San Donato (laps 15 and 23), Savelli to Arrabbiata 1 (lap 18), and the main straight (lap 1, and lap 22 where Capirossi's Ducati drew level by the line). <b>Watch:</b> the position strip is small, so it shows only the shape of the race; the cards
carry the detail.</p>
</div>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="Layout D: wide map-led poster with story column and position strip">{layout_d()}</svg>

<h2>Option B: map + vertical race column</h2>
<div class="grid pros">
<p><b>How it reads:</b> the map on the left says <i>where</i>. On the right, time runs top to
bottom: a vertical position chart (1st on the left) with the 7 story cards beside it, each
linked to its lap. This is your "timeline next to the map", using a familiar chart.</p>
<p><b>Strengths:</b> one meaning per element (map = place, column = time); the race reads like a
TV timing tower. <b>Weak spots:</b> a vertical position chart is less common than a horizontal
one, and the cards are denser than in A.</p>
</div>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="Layout B: map with a vertical lap-by-lap column">{layout_b()}</svg>

<h2>Option C: the race as a ring around Mugello</h2>
<div class="grid pros">
<p><b>How it reads:</b> your idea. The whole race is wrapped once around the circuit,
clockwise from the start line. Each line is a rider, and the closer to the track, the higher
the position. The story cards run in a vertical column on the right.</p>
<p><b>Strengths:</b> striking, unique, and Mugello's shape carries everything. <b>Weak
spots:</b> the lanes can't follow the exact outline (it folds back on itself in the infield,
so they'd cross the track), so they follow a rounded silhouette instead. A spot on the ring
means a <i>time</i>, not a place, so lap 15 sits near Bucine, not San Donato. It needs the
"how to read" note.</p>
</div>
<svg viewBox="0 0 {W} {H}" role="img" aria-label="Layout C: race positions drawn as a ring around the circuit">{layout_c()}</svg>
</main></body></html>
"""
OUT.write_text(html, encoding="utf-8")
print(OUT)
