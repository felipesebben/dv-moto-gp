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
