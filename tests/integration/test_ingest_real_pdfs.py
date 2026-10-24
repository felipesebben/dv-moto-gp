"""Cross-checks between the real Tissot reports. Skipped when data/raw/pdf is empty (e.g. CI)."""

import polars as pl
import pytest

from mugello06 import config, ingest

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (config.RAW_PDF / "classification.pdf").exists(), reason="raw PDFs not present"
    ),
]


@pytest.fixture(scope="module")
def tables() -> dict[str, pl.DataFrame]:
    return ingest.extract()


def test_lap_times_add_up_to_official_race_time(tables: dict[str, pl.DataFrame]) -> None:
    summed = tables["laps"].group_by("rider_number").agg(pl.col("lap_time_s").sum(), laps=pl.len())
    joined = tables["classification"].join(summed, on="rider_number", validate="1:1")
    assert joined.height == tables["classification"].height
    for row in joined.iter_rows(named=True):
        assert row["lap_time_s"] == pytest.approx(row["total_time_s"], abs=1e-3)
        assert row["laps"] == row["laps_completed"]


def test_lap_chart_final_order_matches_classification(tables: dict[str, pl.DataFrame]) -> None:
    final_lap = tables["lap_chart"]["lap"].max()
    chart = tables["lap_chart"].filter(pl.col("lap") == final_lap).sort("position")
    official = tables["classification"].filter(pl.col("laps_completed") == final_lap)
    assert chart["rider_number"].to_list() == official.sort("position")["rider_number"].to_list()


def test_every_lap_chart_rider_is_known(tables: dict[str, pl.DataFrame]) -> None:
    known = set(tables["classification"]["rider_number"])
    assert set(tables["lap_chart"]["rider_number"]) == known
    assert tables["lap_chart"].filter(pl.col("lap") == 0).height == len(known)


def test_official_circuit_facts_agree_with_our_seeds(tables: dict[str, pl.DataFrame]) -> None:
    event = tables["event"].row(0, named=True)
    corners = pl.read_csv(config.SEEDS / "corners.csv").filter(pl.col("turn") > 0)
    assert event["right_corners"] + event["left_corners"] == corners.height
    assert event["track_length_m"] == pytest.approx(
        tables["track_points"]["distance_m"].max(), abs=10
    )
    assert event["race_laps"] == tables["lap_chart"]["lap"].max()
