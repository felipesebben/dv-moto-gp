import duckdb
import pytest

from mugello06 import cli, config


def test_paths_live_under_repo() -> None:
    assert config.RAW_PDF.is_relative_to(config.ROOT)
    assert config.HYPER_PATH.suffix == ".hyper"


def test_cli_rejects_unknown_stage() -> None:
    with pytest.raises(SystemExit):
        cli.main(["nope"])


def test_duckdb_in_memory() -> None:
    with duckdb.connect() as con:
        assert con.execute("select 42").fetchall() == [(42,)]
