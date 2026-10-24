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

## 2. Layout D (landscape, 140 × 80 cm)

| Zone | Content | Place |
|---|---|---|
| A · Title | **The story leads:** a small kicker *MUGELLO 2006* with the Italian livery flash (see §4); the headline **"Lost at San Donato. / Won at San Donato."** on two stacked lines; beside it a discreet line drawing of the real San Donato corner (braking stretch in yellow, badges ④ ⑦); a three-sentence standfirst (stakes, fall, duel, the move); a quiet line *Gran Premio d'Italia Alice, Mugello, Sunday 4 June 2006* | top row |
| B · Images | Rossi's Mugello 2006 helmet (captioned) + 46 logo | top-right, above the story column |
| C · Map (hero) | Mugello in TV orientation, about half the poster. Rossi's stretches painted yellow, numbered badges + callouts, a "how to read" key in the empty bottom-left | centre-left |
| D · Key numbers | 0.575 s, 0.002 s, 5 wins, each with the badge of its moment | right band, beside the map |
| G · Circuit band | An Italy locator (north-up, Mugello marked in Rossi yellow; outline from Natural Earth, public domain), then the facts: full name, town, built 1974, 5,245 m × 14 m, 15 corners (9 right, 6 left), longest straight 1,141 m, race distance and conditions | left band, beside the map |
| E · Story | 7 moments as a list read top to bottom, no boxes: badge, lap, headline, ≤ 200-character story, coloured bar | right column |
| F · Positions | Compact left-to-right strip, badges on the lap axis, plain hint "higher = further ahead" in its title line | under the map |
| Footer | Map key (left, well spaced) + credits (right), with clear air above | bottom edge |

Margins are 65 mm. The badge numbers ①–⑦ are the thread through map → story → positions.

## 3. Typography

**Family:** [Barlow](https://fonts.google.com/specimen/Barlow) and **Barlow Condensed** by
Jeremy Tribby, SIL Open Font License 1.1 (free for print). They're low-contrast grotesques
inspired by road signage, with a motorsport feel and very legible at a distance. Using one
family keeps the poster calm.

| Role | Face | Size (pt) | Notes |
|---|---|---|---|
| Kicker (MUGELLO 2006) | Barlow Condensed ExtraBold Italic | 60 | with the livery flash |
| Headline | Barlow Condensed ExtraBold Italic | 149 | two stacked lines; italic only in the kicker and headline, for a sense of speed |
| Standfirst | Barlow Regular | 32 | primary ink, three sentences |
| Quiet event line | Barlow Regular | 27 | muted ink |
| Key numbers | Barlow SemiBold | 82 | same family as the rest (no display font for figures), proportional digits |
| Story headline | Barlow Condensed SemiBold | 30 | |
| Story text, map key | Barlow Regular | 23 | ≤ 200 characters per story (enforced by a test) |
| Map callouts | Barlow Condensed SemiBold | 27 | |
| Corner names, axis | Barlow Condensed Medium | 21 | tabular digits on the axis only |
| Credits | Barlow Regular | 18 | **absolute minimum size** |

The minimum of 18 pt is for credits only. Anything the reader needs is at least 21 pt, so
it stays legible at about 1.5 m.
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
  140 × 80 cm landscape (grown from 100 × 70, then 120 × 70, for more air).

- **Layout D**: wide, map-led hybrid (see section 2). Options A, B and C are kept in
  `design/wireframe/` for reference. B's top-to-bottom chart felt odd and A was too tall.
  C was parked because the lanes can't follow the outline exactly and the ring felt
  disconnected from the map; its idea survives as the yellow stretches on the track.

- The TV-call quote was tried in the header and dropped (too busy).

- The title area tells the story (headline A), replacing the dot-separated subtitle.

**Open:**
- Final size and paper (matte recommended for dark backgrounds). Title wording and an
  optional dedication line.
