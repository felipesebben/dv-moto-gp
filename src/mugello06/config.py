"""Project paths and constants shared across pipeline stages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW_PDF = DATA / "raw" / "pdf"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
SQL_DIR = ROOT / "sql"
SEEDS = ROOT / "seeds"
TRACK_GEOJSON = SEEDS / "mugello.geojson"

DUCKDB_PATH = INTERIM / "mugello06.duckdb"
HYPER_PATH = PROCESSED / "mugello06.hyper"
POSTER_SCHEMA = "poster"

PROTAGONIST = 46  # Valentino Rossi
RIVAL = 65  # Loris Capirossi
