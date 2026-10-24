# Design standards: Mugello 2006 poster

The rules every poster element follows. Colour figures come from the dataviz skill's
validator (`validate_palette.js`: OKLab ΔE, Machado 2009 colour-vision simulation, WCAG 2
and APCA contrast); they were measured, not eyeballed. The wireframe that applies these
rules is `design/wireframe/poster_d.html` (layout D, chosen), built by
`design/wireframe/tools/build_poster_d.py`.

## 1. Audience and principles

- **One reader:** a lifelong Rossi fan who knows Mugello well but doesn't read charts.
  Every chart must make sense without any data training.
- **Two protagonists:** **Rossi** (always yellow) and **Mugello** (the map is the hero).
- **Emphasis, not categories:** Rossi is highlighted, Capirossi is the one rival colour, and
  everyone else is grey context. No legend of many colours.
- **Numbers tie the layers together:** each key moment has one badge number ①–⑦ that is the
  same on the map, on its story card and on the lap axis. You can read the poster by
  following the numbers alone.
- **Plain words:** positions are "1st, 2nd…", times are "seconds", and there's no jargon
  (gap, delta, sector) in reader-facing text.

## 2. Layout D (landscape, 140 × 110 cm)

Three bands, top to bottom, on a 65 mm margin:

| Band | Content |
|---|---|
| **Header** | *MUGELLO 2006* with the Italian livery flash, the title **THE ROSSI COMEBACK**, then one paragraph: the event and date run in (*Gran Premio d'Italia Alice, 4 June 2006.*), then the stakes, the fall at San Donato, the pass for the win at the same corner, and "Patience, then one perfect move: a race still counted among his greatest." Plain text. |
| **Content band** (about 95 px of air under the header; all three columns share one top line) | **Left: the circuit**, as one group: the Italy locator (Mugello in Rossi yellow; Natural Earth, public domain) with the facts directly under it (full name, town, built 1974, 5,245 m × 14 m, 15 corners: 9 right, 6 left, longest straight 1,141 m, race distance and conditions). **Centre: the map** in TV orientation, with Rossi's stretches in yellow and numbered badges and callouts. **Right: key numbers** in race order, each with its moment's badge: **0.730 s** behind Capirossi after running wide, in 5th (④); **0.002 s** after lap 22 (⑥); **0.575 s** winning margin (⑦). |
| **Race band** | The positions chart, full width (each line a rider; Rossi yellow, Capirossi coral, others grey), with **the 7 moments told along it**. Cards alternate above (laps 1, 13, 18, 23) and below (laps 7, 15, 22) so close laps never collide. **Each card's number sits on a bar in the rider's colour** (yellow for Rossi, coral for Capirossi's charge) **that runs toward the race and lands on the moment's lap**: down from the numbers above the chart, up from the numbers below it. Cards start at their lap and are as wide as the race stretch to the next card on their side; near the right edge they are pulled left and the connector bends to the lap. |
| **Footer** | Map key (left) + credits and a small QR code to the official full-race video (bottom-right, 40 mm). |

No logo or photos: the map, the chart and the text carry the poster. The badge numbers ①–⑦
link the map, the key numbers and the race band. Yellow badge = Rossi moment, coral ring =
Capirossi moment.

## 3. Typography

**Family:** [Barlow](https://fonts.google.com/specimen/Barlow) and **Barlow Condensed** by
Jeremy Tribby, SIL Open Font License 1.1 (free for print). They're low-contrast grotesques
inspired by road signage, with a motorsport feel and very legible at a distance. Using one
family keeps the poster calm.

| Role | Face | Size (pt) | Notes |
|---|---|---|---|
| Header (MUGELLO 2006) | Barlow Condensed ExtraBold Italic | 53 | with the Italian livery flash |
| Title (THE ROSSI COMEBACK) | Barlow Condensed ExtraBold Italic | 220 | one line; italic only in the header and title, for a sense of speed |
| Header paragraph | Barlow Regular; the event and date run in, in Barlow Condensed SemiBold | 35 | primary ink, plain |
| Key numbers | Barlow SemiBold | 82 | same family as the rest, proportional digits |
| Moment headline | Barlow Condensed SemiBold | 34 | |
| Moment text | Barlow Regular | 26 | ≤ 200 characters per moment (enforced by a test) |
| Map callouts | Barlow Condensed SemiBold | 30 | |
| Circuit facts, eyebrows, key labels | Barlow / Barlow Condensed | 27–28 | |
| Corner names, axis, footer, credits, QR caption | Barlow / Barlow Condensed | 25 | **the smallest text on the poster** |

**Floor: nothing on the poster is below 24 pt** (the hard rule is never below 10 pt). The
wireframe generator refuses to build if any text class would print smaller. Use the
wireframe's *Zoom: Print size* to judge sizes on screen.
**Tableau:** install the Barlow TTFs on Windows before building, so Tableau Desktop can use
them; PDF export embeds them.

## 4. Colour

Surface: dark "asphalt". Fluorescent yellow only works on dark: on white paper it
drops to about 1.1:1 contrast.

| Token | Hex | Job | Contrast on surface (WCAG / APCA) |
|---|---|---|---|
| `surface` | `#1C1A19` | background | — |
| `ink` | `#F2EFE9` | primary text, track outline | 15.1 : 1 / Lc −96 |
| `ink-muted` | `#A8A29A` | secondary text, corner names, axis | 6.9 : 1 / Lc −51 |
| `rule` | `#3A3734` | guides, hairlines | (recessive by design) |
| `rossi` | `#FDF504` | **marks only**: Rossi's line, badge fill, card accent | 15.1 : 1 |
| `rival` | `#F26B5B` | Capirossi's line | 5.8 : 1 / Lc −45 |
| `context` | `#6F6A64` | the other riders' lines | 3.2 : 1 ✔ |
| `italy` | `#229457` | finish-line mark only | 4.5 : 1 |
| `rossi-blue` | `#0F8FCD` | reserved (46-logo outline), not used for data | 4.8 : 1 |
| `italy-red` | `#CE2B37` | **decoration only**: the title's tricolore accent | ≥ 3 : 1 |

Sources: yellow, blue and black come from the 46 logo; red and green from the helmet. The
red was then brightened (see below).

**Validator results (dark mode, all pairs, because lines cross):**

| Pair | Normal vision ΔE | Worst colour-blind ΔE | Verdict |
|---|---|---|---|
| Rossi ↔ Capirossi (`#FDF504` / `#F26B5B`) | 34.8 | 25.8 (deuteranopia) | ✔ |
| Capirossi ↔ others (`#F26B5B` / `#6F6A64`) | 23.0 | 9.9 (protanopia) | ✔ (target ≥ 8) |
| ~~helmet red `#B93940` ↔ grey~~ | 20.3 | **3.6** | ✘ **rejected**: Capirossi would vanish into the pack for red-blind readers |

**Italian accent (decoration, never data):** green `#229457`, ink white and flag red `#CE2B37`.
Flag red is kept distinct from Capirossi's coral, but the two are still fairly close (ΔE 13.7, under
the 15 "clearly different" floor). So the accent stays small: the **livery flash** after the title was chosen
(over a tricolore underline and a tricolore "2006", which could read as Capirossi's colour). Green and red look alike to
green-blind readers (ΔE 4.6), which is fine for a flag carrying no information.

**Documented exceptions:**
- `rossi` fails the validator's *lightness band* (L 0.95 > 0.67). That band exists to keep
  colours **equally loud** in multi-colour charts. Here Rossi is *meant* to be the loudest
  mark, so this is a deliberate exception. Every other check passes by a wide margin.
- `rival` sits just above the band too (L 0.69 > 0.67). Pulling it into the band means
  darkening it, and the darker reds we tested (`#E0474C`, `#B93940`) collapse into the grey
  for red-blind readers (ΔE 3.6). Being distinguishable from the grey matters more.
- `context` grey fails the *chroma floor* by design: it's meant to read as "no identity".

## 5. Chart and accessibility rules

1. **Colour is never the only cue.** Riders are named at the line ends ("Rossi · 1st"),
   moments have numbers, and Rossi's line is also the **thickest** (4 px against 3 px and
   1.5 px), so it survives greyscale printing.
2. **Text never uses a data colour.** Labels are in `ink` / `ink-muted`, with a coloured
   dot or line beside them. The only exception is the number *inside* a yellow badge, which
   is near-black (`#1C1A19`, 15 : 1).
3. **Position chart:** 1st at the top, a single y-scale, only the leading 6 riders (fewer
   lines), and no value on every point. Labels go on the line ends only.
4. **Map:** only corners where a moment happened get a badge. All corner names are small and
   muted, so the circuit is recognisable without clutter.
5. **Thin, quiet chrome:** hairline solid guides (never dashed), no gridlines in the
   position chart beyond the key-lap guides.
6. **Proofing checklist before print:** check the wireframe or the final export in
   *Protanopia*, *Deuteranopia* and *Greyscale* (toggles in the wireframe), and do a test
   print of the positions strip (zone F) at 100 % scale to check the 21 pt minimum.

## 6. Decisions

**Agreed:**
- Map orientation follows **TV graphics** (main straight across, north pointing left), never
  north-up. This means the build uses rotated x/y coordinates from the pipeline instead of a
  Tableau map, which can't rotate.
- Keep **all 7 key moments**.
- The poster is **large and airy**: whitespace matters more than density. Sketched at
  140 × 110 cm landscape (grown step by step from 100 × 70, always for more air).

- **Layout D**: wide, map-led hybrid (see section 2). Options A, B and C are kept in
  `design/wireframe/` for reference. B's top-to-bottom chart felt odd and A was too tall.
  C was parked because the lanes can't follow the outline exactly and the ring felt
  disconnected from the map; its idea survives as the yellow stretches on the track.

- The TV-call quote was tried in the header and dropped (too busy).

- The title is **THE ROSSI COMEBACK**, under a small **MUGELLO 2006** header with the
  livery flash, then one paragraph (no separate event line or subtitle). The QR code is small, in the
  bottom-right corner, linking to the official full-race video.

- No imagery: the helmet and then the 46 logo were tried and dropped (too much information).
- The moments are told along the positions chart (a timeline attached to it), replacing the
  separate story column.

- The "5 Mugello wins in a row" figure was replaced by Rossi's 0.730 s deficit after
  running wide: the poster is about 2006 only.

- Moment ② is Capirossi's fastest lap of the race (lap 7), replacing Stoner's crash, so the
  rivalry is told in two steps (②, ③).

**Open:**
- Paper: matte recommended for the dark background.
  No dedication line.
