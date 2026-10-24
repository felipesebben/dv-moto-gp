# Design standards: Mugello 2006 poster

The rules every poster element follows. Colour figures come from the dataviz skill's
validator (`validate_palette.js`: OKLab ΔE, Machado 2009 colour-vision simulation, WCAG 2
and APCA contrast); they were measured, not eyeballed. The wireframe that applies these
rules is `design/wireframe/poster_wireframe.html`.

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

## 2. Layout (A2 portrait, 420 × 594 mm; size still to confirm)

| Zone | Content | Share of height |
|---|---|---|
| A · Header | Title, subtitle, one-sentence lede, 46 logo + helmet images | ~15 % |
| B · Map | Mugello outline with numbered moment badges and short callouts | ~40 % |
| C · Story | 7 cards in lap order (badge, lap, headline, ≤ 200-character story) | ~16 % |
| D · Laps | Shared lap axis (grid → lap 23) with badges, then the position chart | ~17 % |
| E · Numbers | Three key figures + credits | ~7 % |

Margins are 20 mm. Zones C and D share the same horizontal lap scale, so a card's curve
lands on its lap and the guide drops straight into the position chart.

## 3. Typography

**Family:** [Barlow](https://fonts.google.com/specimen/Barlow) and **Barlow Condensed** by
Jeremy Tribby, SIL Open Font License 1.1 (free for print). They're low-contrast grotesques
inspired by road signage, with a motorsport feel and very legible at a distance. Using one
family keeps the poster calm.

| Role | Face | Size at A2 (pt) | Notes |
|---|---|---|---|
| Title | Barlow Condensed ExtraBold Italic | 96 | the only italic, for a sense of speed |
| Subtitle | Barlow Condensed Medium | 28 | |
| Lede | Barlow Regular | 18 | muted ink |
| Card headline | Barlow Condensed SemiBold | 22 | |
| Card story / callouts | Barlow Regular / Condensed SemiBold | 14–16 | ≤ 200 characters per story (enforced by a test) |
| Key numbers | Barlow SemiBold | 60 | same family as the rest (no display font for figures), proportional digits |
| Chart labels, corners, axis | Barlow Condensed Medium | 12–13 | tabular digits on the axis only |
| Credits | Barlow Regular | 9 | **absolute minimum size** |

The minimum of 9 pt is for credits only. Anything the reader needs is at least 12 pt, so
it stays legible at about 1 m.
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

Sources: yellow, blue and black come from the 46 logo; red and green from the helmet. The
red was then brightened (see below).

**Validator results (dark mode, all pairs, because lines cross):**

| Pair | Normal vision ΔE | Worst colour-blind ΔE | Verdict |
|---|---|---|---|
| Rossi ↔ Capirossi (`#FDF504` / `#F26B5B`) | 34.8 | 25.8 (deuteranopia) | ✔ |
| Capirossi ↔ others (`#F26B5B` / `#6F6A64`) | 23.0 | 9.9 (protanopia) | ✔ (target ≥ 8) |
| ~~helmet red `#B93940` ↔ grey~~ | 20.3 | **3.6** | ✘ **rejected**: Capirossi would vanish into the pack for red-blind readers |

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
   print of zone D at 100 % scale to check the 12 pt minimum.

## 6. Decisions

**Agreed:**
- Map orientation follows **TV graphics** (main straight across, north pointing left), never
  north-up. This means the build uses rotated x/y coordinates from the pipeline instead of a
  Tableau map, which can't rotate.
- Keep **all 7 key moments**.
- The poster is **large and airy**: whitespace matters more than density. A2 is the minimum;
  layouts B and C are sketched at 100 × 70 cm landscape.

- **Layout B**: landscape, map on the left, vertical race column on the right (position
  chart running top to bottom + the 7 story cards linked to their laps). Options A and C are
  kept in `design/wireframe/` for reference. C was parked because the lanes can't follow the
  outline exactly and the ring felt disconnected from the map.

**Open:**
- Final size and paper (matte recommended for dark backgrounds). Title wording and an
  optional dedication line.
