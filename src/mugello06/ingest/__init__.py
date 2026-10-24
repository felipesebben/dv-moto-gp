"""Ingest stage: Tissot timing PDFs + circuit outline -> tidy Parquet tables in data/interim."""

import re
from pathlib import Path

import polars as pl

from mugello06 import config
from mugello06.ingest import parsers
from mugello06.ingest.pdf_text import column_lines, lines
from mugello06.ingest.track import parse_outline, parse_track, parse_track_meta


def race_laps(classification_lines: list[str]) -> int:
    for line in classification_lines:
        if m := re.search(r"Classification after (\d+) laps", line):
            return int(m.group(1))
    raise ValueError("race distance not found in classification")


def extract(pdf_dir: Path = config.RAW_PDF) -> dict[str, pl.DataFrame]:
    classification = lines(pdf_dir / "classification.pdf")
    circuit_info = lines(pdf_dir / "circuit+information.pdf")
    return {
        "classification": parsers.parse_classification(classification, race_laps(classification)),
        "lap_chart": parsers.parse_lap_chart(lines(pdf_dir / "lap+chart.pdf")),
        "laps": parsers.parse_analysis(column_lines(pdf_dir / "analysis.pdf")),
        "track_points": parse_track(config.TRACK_GEOJSON),
        "italy_outline": parse_outline(config.ITALY_GEOJSON),
        "event": parsers.parse_event(
            classification + circuit_info, parse_track_meta(config.TRACK_GEOJSON)
        ),
    }


def run(pdf_dir: Path = config.RAW_PDF, out_dir: Path = config.INTERIM) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name, df in extract(pdf_dir).items():
        path = out_dir / f"{name}.parquet"
        df.write_parquet(path)
        written.append(path)
    return written
