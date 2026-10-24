"""Project paths and constants shared across pipeline stages."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
RAW_PDF = DATA / "raw" / "pdf"
RAW_TRACK = DATA / "raw" / "track"
INTERIM = DATA / "interim"
PROCESSED = DATA / "processed"
SQL_DIR = ROOT / "sql"

DUCKDB_PATH = INTERIM / "mugello06.duckdb"
HYPER_PATH = PROCESSED / "mugello06.hyper"

RIDERS_OF_INTEREST = ("ROSSI", "CAPIROSSI")
