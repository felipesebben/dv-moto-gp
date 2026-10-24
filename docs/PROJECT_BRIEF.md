# Project brief — Mugello 2006 poster

## Goal
A **static poster** (a gift) that records and explains the emotion of the 2006 MotoGP
Italian Grand Prix at Mugello: the duel between **Valentino Rossi** and **Loris Capirossi**.

## Visual concept
- **Main element: the Mugello track map.** The story is anchored to the circuit
  (corners, sectors, the main straight, overtaking points).
- **Supporting charts** around the map, one per "emotional beat" of the race
  (start, the gap swinging back and forth, the decisive laps, the finish).
- **Short narrative text** next to each chart explaining what happened and why it mattered.
- Static output → no interactivity. Everything gets printed.

## Pipeline

| # | Stage | Input | Output | Tools |
|---|-------|-------|--------|-------|
| 0 | Research | Articles, race reports, video | `docs/research/*.md` (timeline, quotes, key moments) | — |
| 1 | Ingest | MotoGP results PDFs (classification, analysis/lap times, lap chart, max speeds) + track geometry | Tidy tables in `data/interim/` (Parquet) | Python, pdfplumber, polars |
| 2 | Model | Interim tables | Analytical model in DuckDB (in-memory/file, no persistent server) | DuckDB SQL in `sql/` |
| 3 | Publish | DuckDB model | `data/processed/mugello06.hyper` with every poster metric pre-calculated | Tableau Hyper API |
| 4 | Visualise | `.hyper` | Tableau workbook (`tableau/*.twb`) | Tableau (you build it, I guide) |
| 5 | Compose | Tableau exports | Final poster | Figma (background, typography, layout) |

Principle: **all metrics are computed in the backend** (gaps, deltas, positions per lap,
sector pace…). Tableau only draws.

## Working agreement
- **Branch per piece of work** (`feat/…`, `fix/…`, `chore/…`, `docs/…`), PR into `main`,
  CI must be green. Claude handles git.
- **Tests per stage** — unit tests on small fixtures; integration tests run against the
  real raw data when it's present locally.
- **Lean, clean code**; `uv` for environments; `ruff` + `mypy` + `pytest` in CI.
- **Roles:** Claude writes the pipeline and guides. You provide the raw MotoGP data and
  build the Tableau workbook yourself.
- Raw data and generated files (`.duckdb`, `.hyper`, `.twbx`) are **not committed**.

## Open questions
1. Which raw PDFs exist for 2006 on motogp.com (lap-by-lap analysis? sector times? speed traps?).
   This decides which charts are possible.
2. Track map source — official circuit layout vs. a GeoJSON outline (e.g. a community
   circuits dataset) vs. tracing it in Figma.
3. Poster size/format (A2? 50×70 cm?) — drives the Tableau dashboard dimensions.
