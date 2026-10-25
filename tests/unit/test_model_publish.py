"""Model + publish on a tiny synthetic race (3 riders, 2 laps) with the real seeds."""

import itertools
import math
import re
from pathlib import Path

import duckdb
import polars as pl
import pytest
from tableauhyperapi import Connection, HyperProcess, TableName, Telemetry, escape_name

from mugello06 import config, model, publish
from mugello06.ingest.track import haversine_m, parse_outline, parse_track

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
    pl.DataFrame(
        [
            {
                "event_name": "Test GP",
                "right_corners": 9,
                "left_corners": 6,
                "circuit_name": "Mugello",
                "circuit_town": "Scarperia",
            }
        ]
    ).write_parquet(tmp_path / "event.parquet")
    parse_outline(config.ITALY_GEOJSON).write_parquet(tmp_path / "italy_outline.parquet")
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
    assert tables == [
        "event",
        "key_moments",
        "key_numbers",
        "locator_features",
        "map_features",
        "positions",
        "race_features",
        "riders",
        "timeline",
        "track",
        "track_stretches",
    ]
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
            assert in_hyper == in_duckdb  # key_numbers is empty: this race has no lap 15
        for table in ("map_features", "race_features", "locator_features"):
            definition = hc.catalog.get_table_definition(TableName(table))
            geometry = definition.get_column_by_name("geometry")
            assert geometry is not None and "GEOGRAPHY" in str(geometry.type)


def test_track_is_in_tv_orientation_and_true_to_scale(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        start = con.execute("select x_m, y_m from poster.track where point_idx = 0").fetchone()
        pts = con.execute(
            "select lon, lat, x_m, y_m from poster.track order by point_idx"
        ).fetchall()
        leftmost_corner = con.execute(
            "select corner_name from poster.track where turn is not null order by x_m limit 1"
        ).fetchone()
    assert start == (0.0, 0.0)  # the start line is the origin
    assert leftmost_corner == ("San Donato",)  # north points left, as on TV
    # the rotation keeps distances: each segment matches its great-circle length
    for (lon0, lat0, x0, y0), (lon1, lat1, x1, y1) in itertools.pairwise(pts):
        segment = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
        assert segment == pytest.approx(haversine_m((lon0, lat0), (lon1, lat1)), abs=1)


def test_stretches_follow_the_outline_and_wrap_past_the_line(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        paths = dict(
            con.execute(
                "select stretch_id, list(point_idx order by seq) "
                "from poster.track_stretches group by 1"
            ).fetchall()
        )
        moment_refs = con.execute("select moment_ids from seed_stretches").fetchall()
        moments = {m for (m,) in con.execute("select moment_id from poster.key_moments").fetchall()}
    assert paths[3] == [125, 126, 127, 0]
    assert all(path == sorted(path) for sid, path in paths.items() if sid != 3)
    refs = {int(m) for (ids,) in moment_refs for m in str(ids).split(",")}
    assert refs <= moments


def test_event_counts_corners(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        assert con.execute("select corners from poster.event").fetchone() == (15,)


R = 6378137.0 / 100  # Web Mercator radius per canvas unit, as in sql/00_macros.sql


def wkt_pairs(wkt: str) -> list[tuple[float, float]]:
    return [(float(a), float(b)) for a, b in re.findall(r"(-?[\d.]+) (-?[\d.]+)", wkt)]


def canvas_xy(wkt: str) -> list[tuple[float, float]]:
    """Undo the fake geography: lon/lat on the equator back to canvas x/y."""
    return [
        (R * math.radians(lon), R * math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)))
        for lon, lat in wkt_pairs(wkt)
    ]


def test_map_canvas_has_every_layer(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        layers = dict(
            con.execute("select layer, count(*) from poster.map_features group by 1").fetchall()
        )
        on_map = con.execute("select count(*) from poster.key_moments where on_map").fetchall()
        aligns = con.execute(
            "select distinct align from poster.map_features "
            "where layer in ('corner_label', 'callout')"
        ).fetchall()
    n = on_map[0][0]
    assert layers == {
        "frame": 4, "track": 1, "stretch": 3, "start_line": 1, "corner_dot": 15,
        "corner_label": 16, "leader": n, "badge": n, "callout": n,
    }  # fmt: skip
    assert {a for (a,) in aligns} <= {"left", "center", "right"}


def test_map_canvas_keeps_the_track_true_to_scale(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        (wkt,) = con.execute(
            "select geometry from poster.map_features where layer = 'track'"
        ).fetchall()[0]
        track = con.execute("select x_m, y_m from poster.track order by point_idx").fetchall()
        frame = con.execute(
            "select geometry from poster.map_features where layer = 'frame'"
        ).fetchall()
    for (x, y), (x_m, y_m) in zip(canvas_xy(wkt), track, strict=True):
        assert x == pytest.approx(x_m, abs=0.05) and y == pytest.approx(y_m, abs=0.05)
    corners = [canvas_xy(g)[0] for (g,) in frame]
    width = max(x for x, _ in corners) - min(x for x, _ in corners)
    height = max(y for _, y in corners) - min(y for _, y in corners)
    assert width / height == pytest.approx(1328 / 992, rel=1e-3)  # the Tableau sheet's ratio


def test_riders_for_the_chart(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        rows = con.execute(
            "select display_name, in_chart from poster.riders order by final_position"
        ).fetchall()
    assert rows == [("Rossi", True), ("Capirossi", True), ("Hayden", True)]


def test_locator_marks_mugello_inside_italy(db: Path) -> None:
    with duckdb.connect(db, read_only=True) as con:
        rings = con.execute(
            "select geometry from poster.locator_features where layer = 'italy' order by polygon_id"
        ).fetchall()
        (mugello,) = con.execute(
            "select geometry from poster.locator_features where layer = 'mugello'"
        ).fetchall()[0]
        start = con.execute("select lon, lat from poster.track where point_idx = 0").fetchone()
    assert len(rings) == 3 and start is not None
    ((lon, lat),) = wkt_pairs(mugello)
    assert haversine_m((lon, lat), start) < 1_000  # the marker sits on the circuit
    for (wkt,) in rings:
        pts = wkt_pairs(wkt)
        assert pts[0] == pts[-1]  # closed
        twice_area = sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in itertools.pairwise(pts))
        assert twice_area > 0  # counter-clockwise, so the polygon is Italy, not the rest
    mainland = wkt_pairs(rings[0][0])
    assert min(x for x, _ in mainland) < lon < max(x for x, _ in mainland)
    assert min(y for _, y in mainland) < lat < max(y for _, y in mainland)
