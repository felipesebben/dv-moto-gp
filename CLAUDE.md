# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A data pipeline for a **static, printed poster** about the 2006 MotoGP Italian GP at Mugello
(Rossi beat Capirossi by 0.575 s). It's a gift. The full brief is in `docs/PROJECT_BRIEF.md`,
and the race narrative, checked against the data, is in `docs/research/race_story.md`.

```
Tissot PDFs ──ingest──▶ Parquet ──model──▶ DuckDB ──publish──▶ .hyper ──▶ Tableau ──▶ Figma
```

**All metrics are computed in the pipeline**, and Tableau only draws.

Poster (agreed with the user): *THE ROSSI COMEBACK* at Mugello 2006. A big map marks where
the key moments happened, and a positions chart below tells the 7 moments along the race,
highlighting only Rossi (the protagonist, in his yellow) and Capirossi (the rival), with
everyone else grey. Nothing prints below 24 pt. It's a gift for the user's father, who is a Rossi fan but
not data literate, so keep the charts simple and the text plain. The user builds the Tableau workbook themselves; Claude
guides with instructions and writes the Python/SQL.

## Commands

```bash
uv sync                                   # env (Python 3.12 is pinned for tableauhyperapi)
uv run mugello06 ingest                   # stages: ingest | model | publish | all
uv run pytest                             # all tests
uv run pytest tests/unit/test_parsers.py::test_classification   # single test
uv run pytest -m "not integration"        # skip tests that need the real PDFs
uv run ruff format . && uv run ruff check . && uv run mypy src   # same checks as CI
```

CI (`.github/workflows/ci.yml`) runs `uv sync --locked`, ruff format --check, ruff check, mypy
(strict) and pytest. Pre-commit runs ruff on commit.

## Architecture

- `src/mugello06/config.py` holds every path and constant. Stages read from and write to
  the `config` paths, never hard-coded ones.
- **Ingest** (`src/mugello06/ingest/`) has two layers for the PDFs, plus the track:
  - `pdf_text.py` handles PDF I/O only. `lines()` reads single-column reports.
    `column_lines()` reads the two-column *Chronological Analysis* report, placing the gutter
    on each page halfway between the left "Speed" header and the right "Lap" header (the
    page midpoint cuts through values). `to_seconds()` turns Tissot times like `1'50.195`
    into seconds.
  - `parsers.py` holds **pure functions over `list[str]`** that return polars DataFrames. They
    are unit-testable without PDFs. Each parser matches lines with a regex and ignores the
    rest (headers, footers, copyright text). `parse_analysis` is a state machine: a rider
    header line (`1st 46 …`) sets the current rider for the lap rows that follow.
  - `track.py` turns `seeds/mugello.geojson` into ordered points with distance along the lap.
  - `ingest/__init__.py` maps each source to its parser (`extract()`) and writes
    `data/interim/{classification,lap_chart,laps,track_points,event}.parquet` (`run()`).
    `event` (one row) comes from the classification + *circuit information* PDFs plus the
    GeoJSON's name/town; `parse_event` raises if any fact is missing.
- **Seeds** (`seeds/`) are committed, hand-curated inputs: the circuit outline (MIT, with
  attribution), `corners.csv` (turn to outline point index, map label offsets), `callouts.csv`,
  `key_numbers.csv`, `stretches.csv`, `italy.geojson` and `key_moments.csv` (the
  story beats shown on the poster). Every line in `key_moments.csv` must trace back to
  `docs/research/race_story.md`, and a unit test enforces text-length limits so the poster
  stays readable.
- **Model** (`src/mugello06/model/`): `build()` creates `stg_*` views over the interim Parquet
  and `seed_*` views over the CSVs, sets the DuckDB variables `protagonist`/`rival` from
  `config`, then runs `sql/*.sql` **in filename order** into a freshly dropped `poster` schema.
  `00_macros.sql` defines shared macros; every other file creates one table: `riders` (with
  `role`, `display_name`, `in_chart`), `positions`, `timeline`, `track`, `key_moments` (with the
  focus rider's position and the card side), `track_stretches`, `event`, `locator_features`,
  `key_numbers`, `map_features`, `race_features`. Later files may depend on earlier ones.
- **Publish** (`src/mugello06/publish/`): copies every `poster.*` table to Parquet in a temp
  dir, then into `data/processed/mugello06.hyper` with Hyper's `external()`. Columns named
  `geo_*` (WKT in DuckDB) are cast to Hyper's `GEOGRAPHY`, i.e. Tableau spatial fields; `wkt`
  is the same shape kept as text.
- Join key across all tables: **`rider_number`**. In `lap_chart`, lap 0 is the starting grid.
  `key_moments` get their coordinates from their corner; a moment without a turn appears on
  the timeline only.
- **Map coordinates:** the poster uses the TV orientation (north points left), which Tableau
  maps can't do. So `track`, `key_moments` and `track_stretches` carry `x_m`/`y_m`: metres
  from the start line, `x = -north`, `y = east`. `track_stretches` (from `seeds/stretches.csv`)
  are the yellow segments; they may wrap past the start line, and `seq` is the drawing order.
- **Canvases (how Tableau draws the map and the race band):** `map_features` (metres) and
  `race_features` (poster px) hold every mark of one sheet, one row per item with `layer`,
  `tableau_layer`, `align`, `role`, `label`, `lat`/`lon` (point rows, for `MAKEPOINT`) and
  **one spatial column per Tableau map layer** (`geo_track`, `geo_stretch`…, filled only on that
  layer's rows; there is deliberately no all-in-one geometry field). The flat drawing is passed as **fake geography** on
  the equator (inverse Web Mercator, 1 unit = 100 m; macros in `sql/00_macros.sql`), so one
  Tableau map sheet can stack all layers with Map Layers. Each has a `frame` layer whose aspect
  equals the sheet's (1328 × 992 and 1728 × 560 px), so the canvas fills the sheet at poster
  scale. Placement constants come from the wireframe (`seeds/corners.csv` label offsets,
  `seeds/callouts.csv`, and the px constants in `sql/11_race_features.sql`): change them
  together with `design/wireframe/tools/build_poster_d.py`. `locator_features` is real
  lon/lat geography (Italy polygons, counter-clockwise, plus the Mugello point).
- **Tableau build:** `docs/TABLEAU_GUIDE.md` is the step-by-step guide (data sources, layers,
  dashboard object positions, export). `design/tableau/tools/preview_canvas.py` renders what
  the canvas sheets should look like straight from the `.hyper` (`design/tableau/previews/`).
- **Custom shapes:** marks with more than one colour (numbered badges, rider dots with a ring,
  the Mugello marker) are PNGs in `design/tableau/shapes/Mugello 2006/`, made by
  `design/tableau/tools/make_shapes.py`, because a Tableau mark has one colour and a shape mark
  no border. Rows that use one carry `shape_file` = the file name (macro `shape_name` in
  `sql/00_macros.sql`); a unit test checks every value has its image.
- The design is settled in `docs/DESIGN_STANDARDS.md` (layout D, 120 × 132 cm, on a 4 px spacing grid) with the
  wireframe in `design/wireframe/poster_d.html`. Follow it when building in Tableau.
- Not parsed on purpose, because the data can be derived from the three tables: grid, top
  speed, fastest-lap reports, analysis by lap.

## Data and tests

- `data/raw/pdf/` holds the official 2006 PDFs, which are **git-ignored** (Dorna copyright).
  The `.duckdb`, `.hyper` and `.twbx` outputs are ignored too; only `.twb` workbooks are
  committed.
- `tests/unit/` uses inline text samples copied from the real PDFs. `tests/integration/`
  (marker `integration`) cross-checks the real PDFs and skips itself when they are missing
  (as in CI). The key reconciliation: each rider's summed lap times equal the official race
  time to within 1 ms, and the final lap-chart order equals the classification. Keep these
  passing when changing parsers.
- Any race fact written for the poster must be checked against the data. Facts not in the
  data (e.g. why Rossi lost 1.3 s on lap 15) are marked "needs a source" in the research
  notes.

## Conventions

- DuckDB is 2.x: relations no longer have `fetchone()`. Use
  `con.execute(...).fetchall()` or `rel.limit(1).fetchall()`.
- Ruff line length is 100, mypy is strict, and the code style is lean (no speculative
  abstractions).
- Git workflow: a new branch per piece of work (`feat/`, `fix/`, `chore/`, `docs/`), then a
  PR into `main`. When the user says **"approve and merge"**: check CI, squash-merge, delete
  the branch, then pull `main`.
- Windows dev machine: in Bash use the venv interpreter `.venv/Scripts/python.exe`
  (or `uv run`).
