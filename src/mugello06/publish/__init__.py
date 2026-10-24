"""Publish stage: poster tables in DuckDB -> a single Tableau .hyper file."""

import tempfile
from pathlib import Path

import duckdb
from tableauhyperapi import (
    Connection,
    CreateMode,
    HyperProcess,
    Telemetry,
    escape_name,
    escape_string_literal,
)

from mugello06 import config
from mugello06.model import poster_tables


def run(db_path: Path = config.DUCKDB_PATH, hyper_path: Path = config.HYPER_PATH) -> list[str]:
    """Copy every poster table to the .hyper file via Parquet. Returns the table names."""
    hyper_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        with duckdb.connect(db_path, read_only=True) as con:
            tables = poster_tables(con)
            for table in tables:
                target = (tmp_dir / f"{table}.parquet").as_posix()
                con.execute(f"copy {config.POSTER_SCHEMA}.{table} to '{target}' (format parquet)")
        with (
            HyperProcess(
                Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU, parameters={"log_dir": tmp}
            ) as hyper,
            Connection(hyper.endpoint, hyper_path, CreateMode.CREATE_AND_REPLACE) as hc,
        ):
            for table in tables:
                source = escape_string_literal(str(tmp_dir / f"{table}.parquet"))
                hc.execute_command(
                    f"CREATE TABLE {escape_name(table)} AS (SELECT * FROM external({source}))"
                )
    return tables
