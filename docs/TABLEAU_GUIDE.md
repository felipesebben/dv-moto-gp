# Tableau build guide: THE ROSSI COMEBACK

A step-by-step guide to building the poster in Tableau Desktop from `data/processed/mugello06.hyper`.
The finished dashboard should match the approved wireframe (`design/wireframe/poster_d.html`,
render `design/wireframe/renders/poster_d.png`), and every rule from `docs/DESIGN_STANDARDS.md`
applies. Work through it one session at a time and check each result before you move on.

**Contents**

0. [The idea: two canvases drawn with map layers](#0-the-idea-two-canvases-drawn-with-map-layers)
1. [The data model](#1-the-data-model)
2. [Session 0: setup and smoke test](#2-session-0-setup-and-smoke-test-do-this-first)
3. [Session 1: data sources](#3-session-1-data-sources)
4. [Session 2: the map canvas](#4-session-2-the-map-canvas)
5. [Session 3: the Italy locator and circuit facts](#5-session-3-the-italy-locator-and-circuit-facts)
6. [Session 4: key numbers](#6-session-4-key-numbers)
7. [Session 5: the race canvas](#7-session-5-the-race-canvas)
8. [Session 6: the dashboard](#8-session-6-the-dashboard)
9. [Session 7: proof and export](#9-session-7-proof-and-export)
10. [Reference: colours, type, troubleshooting](#10-reference)

---

## 0. The idea: two canvases drawn with map layers

The two busiest parts of the poster are the **map** and the **race band**. Each one stacks
many kinds of marks: lines, dots, badges, labels. A normal Tableau chart gives you at most two
mark layers (a dual axis). A **map** gives you as many as you like (**Map Layers**,
Tableau 2020.4 and later), each with its own mark type, colour, size and label settings, all
locked to the same coordinates.

The catch is that map layers only work on geography, and both canvases are flat drawings:
the circuit in the TV orientation (north pointing left) and the race chart in poster pixels.
So the pipeline turns each drawing into **fake geography**:

- the drawing is placed on the equator at 0°, 0°;
- its x becomes longitude and its y becomes latitude, through the inverse of the Web Mercator
  projection that Tableau's maps use. When Tableau projects the shapes back, they land exactly
  where they were drawn, at one uniform scale.

You switch the base map off, and what's left is our drawing on a plain background. Every
layer comes from one table with a `layer` column and a ready-made `geometry` column (a Tableau
spatial field), so you never set up paths or point orders. You drag one shape field per layer.

There's a bonus: a map always keeps one unit the same length across and up, so the circuit
can't be squashed by mistake.

| Canvas | Table | Units | Tableau sheet size |
|---|---|---|---|
| Map | `map_features` | metres, TV orientation | **1328 × 992 px** |
| Race band (chart, moment lines, badges, footer key) | `race_features` | poster px | **1728 × 560 px** |

Each table has a `frame` layer: four invisible corner points with the **same aspect ratio as
the sheet**. Tableau zooms to fit what it draws, so the frame fixes the zoom. The canvas then
fills the sheet edge to edge, and one pixel of the sheet is one pixel of the poster.

## 1. The data model

The `.hyper` file holds 11 tables, all built and tested by the pipeline (`uv run mugello06 all`).
Tableau only draws: every number, position and label is computed upstream.

### Tables

| Table | Grain (one row per…) | Key | Used by |
|---|---|---|---|
| `map_features` | map layer item | `layer` + `item` | **Map** sheet: all its layers |
| `race_features` | race band layer item | `layer` + `item` | **Race** sheet: all its layers |
| `locator_features` | Italy polygon, plus the Mugello point | `layer` + `polygon_id` | **Locator** sheet |
| `key_numbers` | key number (3) | `moment_id` | **Key numbers** sheet |
| `event` | the event (1 row) | none | **Circuit facts** sheet |
| `key_moments` | story moment (7) | `moment_id` | **Moment card** text (headline, story, lap); reference |
| `riders` | rider (19) | `rider_number` | reference (names, roles, `in_chart`) |
| `positions` | rider × lap, lap 0 = grid (425) | `rider_number` + `lap` | reference (raw positions behind the race canvas) |
| `timeline` | lap (23) | `lap` | reference (leader, gap between Rossi and Capirossi) |
| `track` | outline point (129) | `point_idx` | reference (circuit points behind the map canvas) |
| `track_stretches` | point of a yellow stretch | `stretch_id` + `seq` | reference |

"Reference" tables aren't drawn directly. They're the building blocks of the canvases, and
they're useful for checking a value or exploring the race in Tableau.

### Columns you'll use

**`map_features` and `race_features`** (same shape):

| Column | Meaning |
|---|---|
| `layer` | what the row draws: `frame`, `track`, `stretch`, `badge`… (lists in sessions 2 and 5) |
| `align` | for text layers, Tableau's horizontal label alignment: `left`, `center` or `right` |
| `item` | readable name of the row (`San Donato`, `moment 4`, `finish Rossi`…) |
| `moment_id` | the story moment (1–7), on moment rows |
| `role` | `protagonist` (Rossi), `rival` (Capirossi) or `other`: drives the colour |
| `label` | the text to show on the mark (corner names, badge numbers, callouts…) |
| `x_m`/`y_m` or `x_px`/`y_px` | canvas position of point rows, for checking only |
| `geometry` | the shape (Tableau spatial type) |

**`locator_features`**: `layer` (`italy` or `mugello`), `label`, `polygon_id`, `geometry`
(real longitude/latitude, north-up).

**`key_numbers`**: `rank` (race order 1–3), `moment_id`, `lap`, `rider_role`, `value_s`,
`value_text` (e.g. `0.730 s`), `label` (e.g. `Rossi's winning margin`).

**`key_moments`**: `moment_id`, `lap`, `headline`, `story`, `rider_role`, `rider_display_name`,
`rider_position` (where that rider was that lap: the race connector ends there), `card_side`
(`above`/`below` the chart), `on_map`, `corner_name`.

**`event`**: `event_name`, `race_date`, `race_laps`, `race_distance_km`, `track_length_m`,
`track_width_m`, `corners`, `right_corners`, `left_corners`, `longest_straight_m`, `constructed`,
`condition`, `air_c`, `track_c`, `circuit_name`, `circuit_town`.

### Tableau data sources

Use **separate data sources**, one per job. The canvases are single tables on purpose: map
layers must come from one data source, and a single table can't duplicate rows through a join.

| Data source | Tables (relationships) | Feeds |
|---|---|---|
| **Map canvas** | `map_features` | Map |
| **Race canvas** | `race_features` | Race |
| **Locator** | `locator_features` | Locator |
| **Key numbers** | `key_numbers` | Key numbers |
| **Event** | `event` | Circuit facts |
| **Race data** (reference) | `positions` → `riders` on `rider_number`; `positions` → `timeline` on `lap`; `timeline` → `key_moments` on `lap` | checking, and copying the card text |
| **Track** (reference) | `track` → `track_stretches` on `point_idx` | checking only |

```
Race data (reference)                          Track (reference)

riders ──rider_number── positions              track ──point_idx── track_stretches
                           │
                          lap
                           │
                        timeline ──lap── key_moments
```

## 2. Session 0: setup and smoke test (do this first)

A short session that settles the things a guide can't promise, before any real building.

### 2.1 Install the fonts

1. Download **Barlow** and **Barlow Condensed** from Google Fonts (SIL Open Font License).
2. Install these styles **for all users** (right-click the file › *Install for all users*):
   - Barlow: Regular, Medium, SemiBold;
   - Barlow Condensed: Medium, SemiBold, Bold, ExtraBold Italic.
3. Restart Tableau Desktop. In any text box, the font list should now show Barlow and Barlow
   Condensed. (Tableau lists them as families, e.g. *Barlow Condensed SemiBold*.)

### 2.2 Refresh the data

```bash
uv run mugello06 all     # writes data/processed/mugello06.hyper
```

### 2.3 Smoke test: the fake-geography map

1. **Connect › To a File › More…** and open `data/processed/mugello06.hyper`.
2. Drag **map_features** onto the canvas. Go to a new sheet.
3. Double-click **Geometry**. Tableau puts *Longitude (generated)* on Columns,
   *Latitude (generated)* on Rows and *COLLECT(Geometry)* on Detail. You should see the
   circuit with the main straight running across, on top of a world map near Africa.
4. **Map › Background Maps › None.** The world disappears and only our drawing stays.

✅ **Pass:** the circuit looks like the poster (San Donato on the left, Arrabbiata on the right).

### 2.4 Smoke test: zoom, fonts and export

1. **Map › Map Options…**: untick *Allow users to pan and zoom*, *Show map search*,
   *Show view toolbar* and *Show map scale*.
2. New dashboard. **Size › Fixed size › Custom: 1920 × 2108.**
3. Drag the sheet in as **Floating**. In the *Layout* pane set **x 296, y 412, w 1328, h 992**.
4. Add a floating **Image** object at x 0, y 0, w 1920, h 2108 with
   `design/wireframe/renders/poster_d_overlay.png` (*Fit image*). Send it to the back
   (it should sit at the bottom of the floating items in the *Layout* pane).
5. Make the sheet transparent: on the sheet, **Format › Shading**, set *Worksheet* and *Pane*
   to **None**. Then, in the dashboard, select the sheet and set its *Background* to **None**.
6. Check that the white track in Tableau sits **on** the track of the overlay image.

✅ **Pass:** the two tracks overlap within a few pixels. If Tableau leaves a margin around the
frame, see *Troubleshooting* at the end.

7. Add a floating **Text** object with *Lap 23* in **Barlow Condensed Medium 10.5 pt** and
   place it on the overlay's *Lap 23* (x ≈ 1544, y ≈ 1764). It should be the same size.
   That confirms the rule **Tableau pt = wireframe px × 0.75**, used throughout this guide.
8. **File › Print to PDF…** (*Entire workbook* off, *Selection*: this dashboard). Under
   *Paper size*, choose **Unspecified**, so the page takes the dashboard's own size. Open the
   PDF and zoom to 800 %: lines and text should stay sharp, because they're vector.

✅ **Pass:** the PDF is one page with the dashboard's proportions (1920 : 2108 = 120 : 131.75 cm),
and it stays sharp when zoomed.

> If any check fails, stop and report it before building more. Each one has a fallback
> (*Troubleshooting*), and it's cheaper to switch now.

Delete the test dashboard and sheet afterwards, but keep the connection.

## 3. Session 1: data sources

Create each data source from the same `.hyper` file (**Data › New Data Source** › the file).
Rename each one (right-click › *Rename*) as in §1.

1. **Map canvas**: drag `map_features` onto the canvas.
2. **Race canvas**: `race_features`.
3. **Locator**: `locator_features`.
4. **Key numbers**: `key_numbers`.
5. **Event**: `event`.
6. **Race data**: drag `positions`, then `riders` next to it. Tableau proposes a relationship:
   set it to `rider_number = rider_number`. Drag `timeline` and relate it to `positions` on
   `lap = lap`. Drag `key_moments` and relate it to `timeline` on `lap = lap`.
7. **Track**: `track`, then `track_stretches` on `point_idx = point_idx`.

In each data source, check the field types. `Geometry` should show the globe icon (spatial);
`lap`, `rank` and `moment_id` should be numbers. Turn `moment_id`, `rank` and `lap` into
**dimensions** (drag them above the line in the Data pane), because they're labels, not
quantities.

Save the workbook as **`design/tableau/mugello06.twb`**. Only `.twb` files are committed;
packaged `.twbx` files and the `.hyper` stay local.

## 4. Session 2: the map canvas

Sheet name: **Map**. Data source: **Map canvas**.

### 4.1 Calculated fields (one per layer)

Each layer gets a calculated field that returns the shape for that layer only. Create them
in the *Map canvas* data source (**Analysis › Create Calculated Field…**):

| Field name | Formula |
|---|---|
| `L · Frame` | `IF [Layer] = 'frame' THEN [Geometry] END` |
| `L · Track` | `IF [Layer] = 'track' THEN [Geometry] END` |
| `L · Stretch` | `IF [Layer] = 'stretch' THEN [Geometry] END` |
| `L · Start line` | `IF [Layer] = 'start_line' THEN [Geometry] END` |
| `L · Leader` | `IF [Layer] = 'leader' THEN [Geometry] END` |
| `L · Corner dot` | `IF [Layer] = 'corner_dot' THEN [Geometry] END` |
| `L · Corner label left` | `IF [Layer] = 'corner_label' AND [Align] = 'left' THEN [Geometry] END` |
| `L · Corner label center` | `IF [Layer] = 'corner_label' AND [Align] = 'center' THEN [Geometry] END` |
| `L · Corner label right` | `IF [Layer] = 'corner_label' AND [Align] = 'right' THEN [Geometry] END` |
| `L · Badge` | `IF [Layer] = 'badge' THEN [Geometry] END` |
| `L · Callout left` | `IF [Layer] = 'callout' AND [Align] = 'left' THEN [Geometry] END` |
| `L · Callout right` | `IF [Layer] = 'callout' AND [Align] = 'right' THEN [Geometry] END` |

Why split labels by alignment? Alignment is set per layer, not per mark, and the labels need
three alignments. For example, *San Donato* sits to the left of its corner (`left`), *Luco*
sits centred under its corner (`center`) and *Casanova* to the right (`right`).

### 4.2 Build the layers

1. Double-click **`L · Frame`**. It becomes the first layer. **Map › Background Maps › None.**
2. Drag **`L · Track`** onto the view and drop it on the **Add a Marks Layer** box that appears
   at the top-left of the map.
3. Repeat for every other `L ·` field **in this order** (bottom to top): Stretch, Start line,
   Leader, Corner dot, Corner label left, Corner label center, Corner label right, Badge,
   Callout left, Callout right. On the *Marks* card, the **top** layer draws on top; drag
   layers to reorder them.
4. Each layer shows a small *N nulls* indicator at the bottom-right (the rows that belong to
   other layers). Right-click it › **Hide indicator**.
5. **Map › Map Options…**: untick everything (pan and zoom, search, toolbar, scale).

### 4.3 Style each layer

Use **Color › More colors…** to type the hex values. Sizes are relative in Tableau: set them
against the overlay in the dashboard (§8) until they match the widths below.

| Layer | Mark | Colour | Size / width | Label |
|---|---|---|---|---|
| Frame | Circle | any | smallest | **opacity 0 %** (invisible) |
| Track | Line (automatic) | `#F2EFE9` ink | ≈ 7 px | none |
| Stretch | Line | `#FDF504` Rossi yellow | ≈ 9 px (wider than the track) | none |
| Start line | Line | `#229457` green | ≈ 6 px | none |
| Leader | Line | `#A8A29A` muted | thinnest (1 px) | none |
| Corner dot | Circle | `#A8A29A` | ≈ 5 px | none |
| Corner label (×3) | Circle | any, **opacity 0 %** | smallest | `label`, Barlow Condensed Medium 10.5 pt, `#A8A29A` |
| Badge | Circle | `#FDF504`; *Border* `#1C1A19` | ≈ 26 px diameter | `label` (the number), Barlow Condensed Bold 9.8 pt, `#1C1A19`, centred |
| Callout (×2) | Circle | any, **opacity 0 %** | smallest | `label`, Barlow Condensed SemiBold 12.8 pt, `#F2EFE9` |

On the **label** layers (corner labels, callouts, badge):

1. Drag **Label** (`label`) onto *Label*.
2. Click *Label* › **Alignment**:
   - *Corner label left* and *Callout left*: Horizontal **Left** (the text ends at the point);
   - *Corner label center*: Horizontal **Center**;
   - *Corner label right* and *Callout right*: Horizontal **Right** (the text starts at the point);
   - *Badge*: Horizontal **Center**, Vertical **Middle**.
   - Use Vertical **Middle** everywhere: the pipeline puts each label point on the middle of
     the text line.
3. Tick **Allow labels to overlap other marks**, otherwise Tableau hides labels that touch
   a line.
4. On *Callout left*, `1 · Rossi leads at home` should end just left of badges ① and ⑥.

The opacity-0 trick shows only the text: the circle is invisible but still carries the label.

All badges on the map are Rossi's moments (①④⑤⑥⑦), so one badge layer is enough here. The
race canvas (session 5) also has Capirossi's.

### 4.4 Sheet formatting

- **Format › Shading**: *Worksheet* and *Pane* **None** (transparent), so the dashboard's
  `#1C1A19` shows through.
- **Format › Borders / Lines**: all **None**.
- **Worksheet › Tooltip…**: untick *Show tooltips*.
- Hide the sheet title (**Worksheet › Show Title** off).

✅ **Check:** the sheet matches `design/tableau/previews/map_canvas.png` (drawn from the same
data by `design/tableau/tools/preview_canvas.py`) and the map in the wireframe:
3 yellow stretches, 15 corner dots, 16 names, 5 badges with leader lines and 5 callouts.

## 5. Session 3: the Italy locator and circuit facts

### 5.1 Locator (real geography)

Sheet **Locator**, data source **Locator**.

1. Calculated fields:
   - `L · Italy` = `IF [Layer] = 'italy' THEN [Geometry] END`
   - `L · Mugello` = `IF [Layer] = 'mugello' THEN [Geometry] END`
2. Double-click `L · Italy`. Put **Polygon Id** on *Detail* so each land mass is its own shape.
   **Map › Background Maps › None.** Fill `#2A2725`, border `#A8A29A` (*Color › Border*).
3. Add `L · Mugello` as a marks layer and duplicate it (right-click the layer › *Duplicate*):
   - **ring**: Circle, size ≈ 18 px, fill opacity 0 %, *Border* `#FDF504`;
   - **dot**: Circle ≈ 7 px, `#FDF504`. Put *Label* (`Mugello`) on *Label*: Barlow Condensed
     SemiBold 12.8 pt, `#F2EFE9`, Horizontal **Right**, Vertical **Middle**.
4. Map Options: untick everything. Shading None, tooltips off, title off.

This map is north-up on purpose: it's a real map of Italy.

### 5.2 Circuit facts (text)

Sheet **Circuit facts**, data source **Event**. Mark type **Text**. Put every field you need on
*Detail* (or on *Text*), then click *Text* › **…** and write the label. Insert the fields with
*Insert ▸*:

```
<Circuit Name>
<Circuit Town>, Tuscany
Built <Constructed> · <Track Length M> m · <Track Width M> m wide
<Corners> corners: <Right Corners> right, <Left Corners> left
Longest straight <Longest Straight M> m
Race: <Race Laps> laps · <Race Distance Km> km
<Condition> · air <Air C> °C · track <Track C> °C
```

- Line 1: Barlow Condensed SemiBold 14.2 pt, `#F2EFE9`. If the circuit name doesn't wrap after
  *Internazionale* in the 264 px column, type it as two lines (*Autodromo Internazionale* /
  *del Mugello*).
- Other lines: Barlow Regular 11.2 pt, `#A8A29A`. Alignment left.
- Number formats (right-click the field on the shelf › *Format…*): `Track Length M` and
  `Longest Straight M` as Number with a thousands separator (5,245 and 1,141); `Race Distance Km`
  with **1 decimal** (120.6); `Constructed` as Number with **no** separator (1974).
- Shading None, title off, tooltips off.

## 6. Session 4: key numbers

Sheet **Key numbers**, data source **Key numbers**: three rows, each a badge, then the value
with its label.

1. Put **Rank** (dimension) on *Rows*. Right-click it › untick **Show Header**.
2. Create `Zero` = `0`. Put it on *Columns* twice. Right-click the second › **Dual Axis**, then
   **Synchronize Axis**. Hide both axes (right-click › untick *Show Header*).
3. Fix the axis range at **−0.1 to 1** (*Edit Axis* › *Fixed*). The badges then sit at the left
   edge, and the text has room to the right.
4. **First marks card (badge):** Circle, `#FDF504`, ≈ 20 px. Put *Moment Id* on *Label*:
   centred, Barlow Condensed Bold 8.5 pt, `#1C1A19`. Colour by *Rider Role* if you prefer
   (all three are Rossi's).
5. **Second marks card (text):** Circle, **opacity 0 %**. Put *Value Text* and *Label* on
   *Label* and edit it to:
   ```
   <Value Text>
   <Label>
   ```
   *Value Text*: Barlow SemiBold 34.5 pt, `#F2EFE9`. *Label*: Barlow Regular 12 pt, `#A8A29A`.
   Alignment Horizontal **Right**, Vertical **Middle**. Tick *Allow labels to overlap*.
6. **Format › Borders**: row dividers None. Shading None, title and tooltips off.
7. Sort *Rank* ascending: 0.730 s (④), 0.002 s (⑥), 0.575 s (⑦), in race order.

In the dashboard, size each row so the value's baseline lands on the overlay's (rows are
104 px apart in the wireframe).

## 7. Session 5: the race canvas

Sheet **Race**, data source **Race canvas**. The same technique as the map, in poster pixels.

### 7.1 Calculated fields

| Field name | Formula |
|---|---|
| `R · Frame` | `IF [Layer] = 'frame' THEN [Geometry] END` |
| `R · Axis` | `IF [Layer] IN ('axis', 'tick') THEN [Geometry] END` |
| `R · Lines back` | `IF [Layer] = 'line' AND [Role] <> 'protagonist' THEN [Geometry] END` |
| `R · Halo` | `IF [Layer] = 'halo' THEN [Geometry] END` |
| `R · Line Rossi` | `IF [Layer] = 'line' AND [Role] = 'protagonist' THEN [Geometry] END` |
| `R · Connector` | `IF [Layer] = 'connector' THEN [Geometry] END` |
| `R · Rider dot` | `IF [Layer] = 'rider_dot' THEN [Geometry] END` |
| `R · Badge Rossi` | `IF [Layer] = 'badge' AND [Role] = 'protagonist' THEN [Geometry] END` |
| `R · Badge Capirossi` | `IF [Layer] = 'badge' AND [Role] = 'rival' THEN [Geometry] END` |
| `R · Axis label left` | `IF [Layer] = 'axis_label' AND [Align] = 'left' THEN [Geometry] END` |
| `R · Axis label center` | `IF [Layer] = 'axis_label' AND [Align] = 'center' THEN [Geometry] END` |
| `R · End label` | `IF [Layer] = 'end_label' THEN [Geometry] END` |
| `R · Key line` | `IF [Layer] = 'key_line' THEN [Geometry] END` |
| `R · Key label` | `IF [Layer] = 'key_label' THEN [Geometry] END` |

### 7.2 Layers, bottom to top, and their style

Build them as in §4.2: double-click `R · Frame`, set **Background Maps › None**, then add each
field as a marks layer in this order:

| Layer | Mark | Colour | Size | Label / notes |
|---|---|---|---|---|
| Frame | Circle | any | smallest | opacity 0 % |
| Axis | Line | `#A8A29A` | 1 px | the axis line and the 24 lap ticks |
| Connector | Line | **Role** on *Color*: protagonist `#FDF504`, rival `#F26B5B` | 1.5 px, opacity 85 % | moment lines from the badge to the rider (under the riders' lines) |
| Lines back | Line | **Role** on *Color*: other `#6F6A64`, rival `#F26B5B` | other 1.5 px, Capirossi 3 px (**Role** on *Size*) | 4 grey riders + Capirossi |
| Halo | Line | `#1C1A19` (background) | ≈ 7 px | makes Rossi's line read as on top where lines cross |
| Line Rossi | Line | `#FDF504` | ≈ 4 px (the thickest rider line) | |
| Rider dot | Circle | **Role** on *Color* (same two colours); *Border* `#1C1A19` | ≈ 10 px | where the rider was at each moment, plus Rossi and Capirossi at the finish |
| Badge Rossi | Circle | `#FDF504`; *Border* `#1C1A19` | ≈ 24 px | *Label* = `label`: Barlow Condensed Bold 9.8 pt `#1C1A19`, centred. Includes the "4" in the footer key |
| Badge Capirossi | Circle | `#1C1A19`; *Border* `#F26B5B` | ≈ 24 px | *Label* = `label` in `#F2EFE9`, centred. Includes the "2" in the footer key |
| Axis label left | Circle, opacity 0 % | | smallest | `label` (Grid, 1st, 4th, 8th): Barlow Condensed Medium 10.5 pt, `#A8A29A`, Horizontal **Left** |
| Axis label center | Circle, opacity 0 % | | smallest | `Lap 23`, same font, **Center** |
| End label | Circle, opacity 0 % | | smallest | `Rossi · 1st`, `Capirossi · 2nd`: Barlow Condensed SemiBold 11.2 pt, `#F2EFE9`, **Right** |
| Key line | Line | `#FDF504` | ≈ 6 px | the "where it happened" sample in the footer key |
| Key label | Circle, opacity 0 % | | smallest | Barlow Regular 10.5 pt, `#A8A29A`, **Right** |

For every label layer: Vertical **Middle**, and tick **Allow labels to overlap other marks**.
Hide all *nulls* indicators, untick everything in Map Options, and set shading None. Tooltips
and title off.

> **Tip, mark borders:** *Color › Border* applies to the whole layer. That's why Rossi's and
> Capirossi's badges are separate layers: Capirossi's badge is a dark circle with a coral ring.

✅ **Check:** the sheet matches `design/tableau/previews/race_canvas.png`: 6 rider lines (Rossi on top), 7 vertical moment lines, each ending on a dot on its
rider's line (② on Capirossi in 7th at lap 7; ③ on Capirossi in 3rd at lap 13), 7 numbered
badges at the top and bottom edges, and the key at the bottom-left.

## 8. Session 6: the dashboard

### 8.1 Canvas

- New dashboard **Poster**. **Size › Fixed size › Custom: 1920 × 2108** px.
  This is the wireframe's 4 px grid at 1.6 px/mm; it prints at 120 × 131.75 cm.
- **Format › Dashboard › Dashboard shading**: `#1C1A19`.
- Make **every** object **Floating**, and type positions in the *Layout* pane. Every value
  below comes from the wireframe, so it sits on the 4 px grid.
- For each sheet: background None, outer and inner padding 0, borders None, title hidden.
- First add the **overlay** (`design/wireframe/renders/poster_d_overlay.png`, x 0, y 0,
  w 1920, h 2108) at the **back**, to align against. Delete it before exporting.

### 8.2 Object positions

`x, y` is the top-left corner. Text objects show their target **baseline** too: Tableau places
text by its box, so nudge the box until the baseline sits on the overlay's.

| Object | Type | x | y | w | h | Notes |
|---|---|---|---|---|---|---|
| Kicker *MUGELLO 2006* | Text | 96 | 92 | 400 | 36 | baseline 120 · Barlow Condensed ExtraBold Italic 22.5 pt `#F2EFE9` |
| Livery flash | Image `design/tableau/assets/livery_flash.png` | ≈ 276 | 96 | 38 | 24 | 12 px after the kicker's end; match the overlay |
| Title *THE ROSSI COMEBACK* | Text | 90 | 128 | 1200 | 128 | baseline 240 · Barlow Condensed ExtraBold Italic 93 pt `#F2EFE9` (x 90: optical alignment of the italic T) |
| Paragraph | Text | 96 | 272 | 1408 | 92 | 3 lines · run-in *Gran Premio d'Italia Alice, 4 June 2006.* in Barlow Condensed SemiBold 15 pt, the rest Barlow Regular 15 pt, `#F2EFE9` |
| **Map** | Sheet | 296 | 412 | 1328 | 992 | the map box (392, 508, 1136 × 800) plus 96 px of label room on every side |
| *THE CIRCUIT* | Text | 96 | 818 | 264 | 24 | baseline 832 · Barlow Condensed SemiBold 11.2 pt `#A8A29A`, letter-spaced |
| **Locator** | Sheet | 96 | 852 | 232 | 232 | Italy fits in this square box |
| **Circuit facts** | Sheet | 96 | 1104 | 264 | 204 | the first line's baseline is at 1124; the block ends on the map's bottom (1308) |
| **Key numbers** | Sheet | 1560 | 508 | 264 | 312 | first value's baseline at 544, then 648 and 752 |
| *THE RACE, LAP BY LAP* | Text | 96 | 1420 | 1300 | 24 | baseline 1436 · eyebrow + hint (*· each line is a rider, higher = further ahead · numbers match the map*, Barlow Regular 11.2 pt) |
| **Race** | Sheet | 96 | 1460 | 1728 | 560 | from the top cards' badges to the footer key |
| Card ① *LAP 1* | Text | 245 | 1458 | 448 | 132 | |
| Card ③ *LAP 13* | Text | 975 | 1458 | 256 | 132 | |
| Card ⑤ *LAP 18* | Text | 1280 | 1458 | 256 | 132 | |
| Card ⑦ *LAP 23* | Text | 1584 | 1458 | 240 | 132 | |
| Card ② *LAP 7* | Text | 610 | 1802 | 439 | 132 | |
| Card ④ *LAP 15* | Text | 1097 | 1802 | 378 | 132 | |
| Card ⑥ *LAP 22* | Text | 1523 | 1802 | 301 | 132 | |
| Credits | Text | 736 | 1960 | 1000 | 64 | right-aligned: *Watch the race* (baseline 1980), then the credits line (baseline 2012) · Barlow Regular 10.5 pt `#A8A29A` |
| QR code | Image `design/tableau/assets/qr_full_race.png` | 1760 | 1952 | 64 | 64 | 40 mm in print. Links to https://www.youtube.com/watch?v=UP4cYHj8IFs |

Each card's badge (the number) is drawn by the **Race** sheet, 24 px to the left of the text box.
The text boxes overlap the transparent Race sheet, which is fine as long as the cards are
**above** the Race sheet in the *Layout* pane's floating order.

### 8.3 Card text

Copy each card's text from **`key_moments`**. In the *Race data* data source, right-click
`key_moments` › **View Data**, or use this table:

| Card | First line (two styles) | Body |
|---|---|---|
| ① | `LAP 1` + `Rossi leads at home` | From third on the grid, Rossi takes the lead on the first lap in front of his fans. Capirossi, who started second, drops to eighth. |
| ② | `LAP 7` + `Fastest lap of the race` | Seventh and 1.75 seconds behind Rossi, Capirossi sets the fastest lap of the race, 1'50.195. His charge has begun. |
| ③ | `LAP 13` + `Capirossi's charge` | Lap after lap, Capirossi climbs to third and cuts the gap to Rossi from 2 seconds to 0.3. |
| ④ | `LAP 15` + `Rossi runs wide` | Into San Donato Rossi runs wide and almost stops. Four riders go past: from first to fifth. Capirossi takes the lead. |
| ⑤ | `LAP 18` + `The comeback` | Rossi fights back past Gibernau, Melandri and Hayden. At Arrabbiata he is second again, right behind Capirossi. |
| ⑥ | `LAP 22` + `Two thousandths` | Rossi takes the lead, Capirossi takes it back. They cross the line 0.002 seconds apart. |
| ⑦ | `LAP 23` + `Victory at San Donato` | Last lap: Capirossi runs wide at San Donato, the corner where Rossi lost the lead. Rossi goes through and wins by 0.575 seconds. |

Styles:

- `LAP n`: Barlow Condensed Medium 10.5 pt, `#A8A29A`, letter-spaced.
- The headline: Barlow Condensed SemiBold 14.2 pt, `#F2EFE9`.
- The body: Barlow Regular 10.9 pt, `#F2EFE9`, left-aligned.
- Card padding 0. If the seed text changes, update the cards from the table: it's the source
  of truth.

Credits line text: *Data: official MotoGP timing (Tissot / Dorna) · Track: bacinger/f1-circuits
(MIT) · Story: MotoGP broadcast, Paddock Pass Podcast*.

### 8.4 Align against the overlay

With the overlay at the back:

1. **Map and Race:** marks should sit on the overlay's marks. If the whole drawing is a little
   small or offset, see *Troubleshooting › Frame doesn't fill the sheet*.
2. **Line widths and dot sizes:** adjust each layer's *Size* until it covers the overlay's line
   exactly (track 7 px, stretches 9, Rossi 4, Capirossi 3, others 1.5).
3. **Text:** nudge boxes until the baselines match.
4. Hide the overlay (or delete it) and look at the poster on its own.

## 9. Session 7: proof and export

1. **Proof** the dashboard against `docs/DESIGN_STANDARDS.md` §5:
   - nothing is smaller than the corner names (10.5 pt in Tableau = 25 pt in print);
   - Rossi is the only yellow, Capirossi the only coral, everyone else grey;
   - badge numbers match across the map, the key numbers and the race band.
2. **Colour-vision check:** export a PNG (**Dashboard › Export Image…**) and look at it in a
   simulator (e.g. Coblis), in protanopia, deuteranopia and greyscale. Capirossi's coral must
   stay distinct from the grey riders.
3. **Delete the overlay image.**
4. **File › Print to PDF**, *Paper size* **Unspecified**, one page.
5. Send the PDF to the printer at **120 × 131.75 cm**, scaled proportionally, on **matte**
   paper. Ask for a hard proof, and do a 100 % test print of the race band to check the
   smallest text.
6. Commit `design/tableau/mugello06.twb` on a `feat/` branch and open a PR.

## 10. Reference

### Colours

| Token | Hex | Used for |
|---|---|---|
| surface | `#1C1A19` | dashboard background, halo, badge borders, numbers on yellow |
| ink | `#F2EFE9` | track, titles, primary text |
| ink-muted | `#A8A29A` | corner names, axis, secondary text, leader lines |
| rossi | `#FDF504` | Rossi's line, stretches, badges, dots (marks only, never text) |
| rival | `#F26B5B` | Capirossi's line, ring and dots |
| context | `#6F6A64` | the other riders' lines |
| green | `#229457` | the finish line, the livery flash |
| flag red | `#CE2B37` | the livery flash only |
| Italy fill | `#2A2725` | the locator's land |

### Type sizes

The dashboard is 1920 px wide and prints 120 cm wide, so one dashboard pixel is 0.625 mm.
**Tableau pt = wireframe px × 0.75**, and **print pt = Tableau pt × 2.36**.

| Role | Face | Tableau pt | Print pt |
|---|---|---|---|
| Title | Barlow Condensed ExtraBold Italic | 93 | 220 |
| Key numbers | Barlow SemiBold | 34.5 | 82 |
| Kicker | Barlow Condensed ExtraBold Italic | 22.5 | 53 |
| Paragraph | Barlow Regular / Condensed SemiBold run-in | 15 | 35 |
| Circuit name, card headlines | Barlow Condensed SemiBold | 14.2 | 34 |
| Callouts, place name | Barlow Condensed SemiBold | 12.8 | 30 |
| Key-number labels | Barlow Regular | 12 | 28 |
| Eyebrows, facts, end labels | Barlow / Barlow Condensed | 11.2 | 27 |
| Card body | Barlow Regular | 10.9 | 26 |
| Corner names, axis, footer, `LAP n` | Barlow / Barlow Condensed | 10.5 | 25 (the floor) |

### Troubleshooting

**The map shows a world map, or nothing.** Set **Map › Background Maps › None**. If the circuit
is tiny in the middle of the sheet, a layer without a filter is drawing every row: check that
each layer uses its own `L ·`/`R ·` field and not `Geometry`.

**Frame doesn't fill the sheet.** Tableau may leave a small margin when it zooms to fit. First
check the sheet's size in the *Layout* pane, and that inner and outer padding are 0. If a
margin remains, measure it against the overlay, then make the sheet bigger by that margin on
each side (and move it up and left by the same amount). The drawing keeps its scale, so
everything lines up again.

**A calculated field won't return `[Geometry]` inside `IF`.** On older Tableau versions,
ask Claude to split `geometry` into one spatial column per layer in the pipeline. Then each
layer is a plain drag, with no calculations.

**Labels disappear.** Tick *Label › Allow labels to overlap other marks* on that layer.

**Mark sizes jump when the dashboard is resized.** Fix the dashboard size first (8.1), then
set sizes. Don't use *Automatic* sizing.

**The data changed** (e.g. new seed text). Run `uv run mugello06 all`, then in Tableau
**Data › (each data source) › Refresh**. The canvases redraw by themselves; card text objects
need a manual update (§8.3).

**Why not plain x/y charts?** They work for one or two layers (dual axis) but not for the
map's twelve. Use *Track* (`track`: `x_m` on Columns, `y_m` on Rows, Line mark, Path =
`point_idx`, equal fixed axis ranges) only as a fallback.
