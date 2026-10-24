import polars as pl
import pytest

from mugello06 import config
from mugello06.ingest.track import haversine_m, parse_outline, parse_track

OFFICIAL_LAP_M = 5245
POSTER_TEXT_LIMITS = {"headline": 25, "story": 200}  # keep the poster readable


@pytest.fixture(scope="module")
def track() -> pl.DataFrame:
    return parse_track(config.TRACK_GEOJSON)


def test_haversine_one_degree_of_latitude() -> None:
    assert haversine_m((0.0, 0.0), (0.0, 1.0)) == pytest.approx(111_195, rel=1e-3)


def test_track_is_a_closed_loop_of_official_length(track: pl.DataFrame) -> None:
    first, last = track.row(0, named=True), track.row(-1, named=True)
    assert (first["lon"], first["lat"]) == (last["lon"], last["lat"])
    assert last["distance_m"] == pytest.approx(OFFICIAL_LAP_M, abs=10)
    assert track["distance_m"].is_sorted()


def test_corners_cover_every_turn_in_order(track: pl.DataFrame) -> None:
    corners = pl.read_csv(config.SEEDS / "corners.csv")
    assert corners["turn"].to_list() == list(range(16))
    assert corners["point_idx"].is_sorted() and corners["point_idx"].is_unique().all()
    assert corners["point_idx"].max() < track.height


def test_key_moments_reference_real_laps_and_turns() -> None:
    moments = pl.read_csv(config.SEEDS / "key_moments.csv")
    turns = set(pl.read_csv(config.SEEDS / "corners.csv")["turn"])
    assert moments["lap"].is_sorted() and moments["lap"].is_between(1, 23).all()
    assert set(moments["turn"].drop_nulls()) <= turns
    for column, limit in POSTER_TEXT_LIMITS.items():
        too_long = moments.filter(pl.col(column).str.len_chars() > limit)[column].to_list()
        assert not too_long, f"{column} over {limit} chars: {too_long}"


def test_italy_outline_has_mainland_and_islands_as_closed_rings() -> None:
    italy = parse_outline(config.ITALY_GEOJSON)
    assert italy["polygon_id"].n_unique() == 3  # mainland, Sicily, Sardinia
    for _, ring in italy.group_by("polygon_id"):
        ring = ring.sort("point_idx")
        assert ring.row(0)[2:] == ring.row(-1)[2:]  # first point == last point
    assert italy["lat"].is_between(35, 48).all() and italy["lon"].is_between(6, 19).all()
