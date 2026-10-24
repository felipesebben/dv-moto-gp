"""Model stage: interim Parquet + seeds -> poster tables in DuckDB (one SQL file per table)."""

from pathlib import Path

import duckdb

from mugello06 import config

STAGING = ("classification", "lap_chart", "laps", "track_points")
SEEDS = ("corners", "key_moments")


def build(
    con: duckdb.DuckDBPyConnection,
    interim: Path = config.INTERIM,
    seeds: Path = config.SEEDS,
    sql_dir: Path = config.SQL_DIR,
) -> list[str]:
    """Create staging views, then run sql/*.sql in order. Returns the poster table names."""
    con.execute(f"create schema if not exists {config.POSTER_SCHEMA}")
    con.execute(f"set variable protagonist = {config.PROTAGONIST}")
    con.execute(f"set variable rival = {config.RIVAL}")
    for name in STAGING:
        path = (interim / f"{name}.parquet").as_posix()
        con.execute(f"create or replace view stg_{name} as select * from read_parquet('{path}')")
    for name in SEEDS:
        path = (seeds / f"{name}.csv").as_posix()
        con.execute(f"create or replace view seed_{name} as select * from read_csv('{path}')")
    for sql in sorted(sql_dir.glob("*.sql")):
        con.execute(sql.read_text(encoding="utf-8"))
    return poster_tables(con)


def poster_tables(con: duckdb.DuckDBPyConnection) -> list[str]:
    rows = con.execute(
        "select table_name from information_schema.tables "
        "where table_schema = ? and table_type = 'BASE TABLE' order by table_name",
        [config.POSTER_SCHEMA],
    ).fetchall()
    return [name for (name,) in rows]


def run(db_path: Path = config.DUCKDB_PATH) -> list[str]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(db_path) as con:
        return build(con)
