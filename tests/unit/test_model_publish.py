"""Model + publish on a tiny synthetic race (3 riders, 2 laps) with the real seeds."""

from pathlib import Path

import duckdb
import polars as pl
import pytest
from tableauhyperapi import Connection, HyperProcess, Telemetry, escape_name

from mugello06 import config, model, publish
from mugello06.ingest.track import parse_track

RIDERS = {46: ("Valentino", "ROSSI"), 65: ("Loris", "CAPIROSSI"), 69: ("Nicky", "HAYDEN")}
# lap -> finishing order; Capirossi leads lap 1, Rossi wins on lap 2
ORDER = {0: [65, 46, 69], 1: [65, 46, 69], 2: [46, 65, 69]}
LAP_TIMES = {46: [111.0, 110.0], 65: [110.5, 111.0], 69: [112.0, 112.0]}


@pytest.fixture
def interim(tmp_path: Path) -> Path:
    pl.DataFrame(
        [
            {
                "rider_number": n,
                "first_name": first,
                "surname": last,
                "nation": "ITA",
                "team": "T",
                "motorcycle": "M",
                "status": "classified",
                "position": ORDER[2].index(n) + 1,
            }
            for n, (first, last) in RIDERS.items()
        ]
    ).write_parquet(tmp_path / "classification.parquet")
    pl.DataFrame(
        [
            {"lap": lap, "position": pos, "rider_number": n}
            for lap, order in ORDER.items()
            for pos, n in enumerate(order, start=1)
        ]
    ).write_parquet(tmp_path / "lap_chart.parquet")
    pl.DataFrame(
        [
            {"rider_number": n, "lap": lap, "lap_time_s": t}
            for n, times in LAP_TIMES.items()
            for lap, t in enumerate(times, start=1)
        ]
    ).write_parquet(tmp_path / "laps.parquet")
    parse_track(config.TRACK_GEOJSON).write_parquet(tmp_path / "track_points.parquet")
    return tmp_path


@pytest.fixture
def db(interim: Path) -> Path:
    path = interim / "test.duckdb"
    with duckdb.connect(path) as con:
        model.build(con, interim=interim)
    return path


def test_timeline_follows_protagonist_and_rival(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        rows = con.execute(
            "select lap, protagonist_leads, protagonist_position, rival_position, "
            "rival_minus_protagonist_s, headline from poster.timeline order by lap"
        ).fetchall()
    assert rows == [
        (1, False, 2, 1, -0.5, "Rossi leads at home"),
        (2, True, 1, 2, 0.5, None),
    ]


def test_roles_and_positions(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        roles = dict(con.execute("select rider_number, role from poster.riders").fetchall())
        grid = con.execute(
            "select rider_name from poster.positions where lap = 0 order by position"
        ).fetchall()
    assert roles == {46: "protagonist", 65: "rival", 69: "other"}
    assert grid[0] == ("Loris CAPIROSSI",)


def test_key_moments_get_map_coordinates_from_their_corner(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        located = con.execute(
            "select count(*) filter (where turn is not null and lon is null), "
            "count(*) filter (where turn is null and lon is not null) from poster.key_moments"
        ).fetchone()
    assert located == (0, 0)


def test_publish_writes_every_poster_table_to_hyper(db: Path, tmp_path: Path) -> None:
    hyper_path = tmp_path / "test.hyper"
    tables = publish.run(db_path=db, hyper_path=hyper_path)
    assert tables == ["key_moments", "positions", "riders", "timeline", "track"]
    with (
        HyperProcess(
            Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters={"log_dir": str(tmp_path)}
        ) as hyper,
        Connection(hyper.endpoint, hyper_path) as hc,
        duckdb.connect(db, read_only=True) as con,
    ):
        for table in tables:
            in_hyper = hc.execute_scalar_query(f"SELECT COUNT(*) FROM {escape_name(table)}")
            in_duckdb = con.execute(f"select count(*) from poster.{table}").fetchall()[0][0]
            assert in_hyper == in_duckdb > 0
