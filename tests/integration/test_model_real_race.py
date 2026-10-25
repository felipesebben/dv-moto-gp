"""The poster's story, checked against the modelled real data. Skipped without the raw PDFs."""

from pathlib import Path

import duckdb
import pytest

from mugello06 import config, ingest, model

pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (config.RAW_PDF / "classification.pdf").exists(), reason="raw PDFs not present"
    ),
]


@pytest.fixture(scope="module")
def con(tmp_path_factory: pytest.TempPathFactory) -> duckdb.DuckDBPyConnection:
    interim: Path = tmp_path_factory.mktemp("interim")
    ingest.run(out_dir=interim)
    connection = duckdb.connect()
    model.build(connection, interim=interim)
    return connection


def lap(con: duckdb.DuckDBPyConnection, n: int) -> tuple[object, ...]:
    row = con.execute(
        "select protagonist_position, rival_position, rival_minus_protagonist_s "
        "from poster.timeline where lap = ?",
        [n],
    ).fetchone()
    assert row is not None
    return tuple(row)


@pytest.mark.parametrize(
    ("n", "expected"),
    [
        (1, (1, 8, 2.205)),  # Rossi leads, Capirossi 8th
        (14, (1, 3, 0.157)),  # Capirossi right behind
        (15, (5, 1, -0.73)),  # Rossi runs wide at San Donato
        (18, (2, 1, -0.124)),  # the comeback
        (22, (2, 1, -0.002)),  # two thousandths
        (23, (1, 2, 0.575)),  # victory
    ],
)
def test_story_beats(con: duckdb.DuckDBPyConnection, n: int, expected: tuple[object, ...]) -> None:
    assert lap(con, n) == expected


def test_every_key_moment_lands_on_the_timeline(con: duckdb.DuckDBPyConnection) -> None:
    flagged = con.execute("select count(*) from poster.timeline where is_key_moment").fetchall()
    moments = con.execute("select count(*) from poster.key_moments").fetchall()
    assert flagged == moments


def test_moments_point_at_their_rider(con: duckdb.DuckDBPyConnection) -> None:
    rows = con.execute(
        "select rider_display_name, rider_position, card_side "
        "from poster.key_moments order by moment_id"
    ).fetchall()
    assert [r[:2] for r in rows] == [
        ("Rossi", 1),
        ("Capirossi", 7),  # fastest lap, in 7th
        ("Capirossi", 3),  # the charge, up to 3rd
        ("Rossi", 5),  # ran wide, down to 5th
        ("Rossi", 2),
        ("Rossi", 2),
        ("Rossi", 1),
    ]
    assert [r[2] for r in rows] == ["above", "below"] * 3 + ["above"]


def test_key_numbers(con: duckdb.DuckDBPyConnection) -> None:
    rows = con.execute("select moment_id, value_text from poster.key_numbers order by rank")
    assert rows.fetchall() == [(4, "0.730 s"), (6, "0.002 s"), (7, "0.575 s")]


def test_race_canvas_connectors_land_on_the_rider_lines(con: duckdb.DuckDBPyConnection) -> None:
    layers = dict(
        con.execute("select layer, count(*) from poster.race_features group by 1").fetchall()
    )
    assert layers["line"] == 6 and layers["connector"] == 7 and layers["badge"] == 7 + 2  # + key
    # each connector ends exactly on its rider's line at that lap (the line has 10 points a lap)
    ends = con.execute(
        """
        select
            string_split(trim(c.wkt, 'LINESTRING()'), ', ')[2],
            string_split(trim(l.wkt, 'LINESTRING()'), ', ')[m.lap * 10 + 1]
        from poster.race_features as c
        join poster.key_moments as m on c.moment_id = m.moment_id
        join poster.race_features as l on l.layer = 'line' and l.item = m.rider_display_name
        where c.layer = 'connector'
        """
    ).fetchall()
    assert len(ends) == 7 and all(end == point for end, point in ends)
