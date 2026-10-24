# dv-moto-gp — Mugello 2006

Data pipeline behind a static poster of the 2006 MotoGP Italian GP at Mugello
(Rossi vs Capirossi). See [docs/PROJECT_BRIEF.md](docs/PROJECT_BRIEF.md) for the full brief.

```
PDFs (motogp.com) ──ingest──▶ Parquet ──model──▶ DuckDB ──publish──▶ .hyper ──▶ Tableau ──▶ Figma poster
```

## Layout

```
src/mugello06/
  ingest/    PDF + track parsing → data/interim/*.parquet
  model/     DuckDB modelling (runs sql/*.sql)
  publish/   DuckDB → data/processed/mugello06.hyper
sql/         modelling queries, one file per table
tests/
  unit/        fast, fixture-based
  integration/ run against real data in data/raw (skipped if missing)
  fixtures/    tiny sample inputs
data/        raw / interim / processed — git-ignored
docs/research/  race history, timeline, sources
tableau/     .twb workbooks (packaged .twbx are ignored)
design/figma/   poster design notes/exports
```

## Setup

```bash
uv sync                      # creates .venv with runtime + dev deps
uv run pre-commit install    # format/lint on every commit
```

## Run

```bash
uv run mugello06 ingest | model | publish | all
uv run pytest
uv run ruff check . && uv run ruff format --check . && uv run mypy src
```

## Workflow
Every change lives on its own branch (`feat/…`, `fix/…`, `chore/…`, `docs/…`) and merges
into `main` via PR once CI (lint, types, tests) is green.
