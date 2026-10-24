"""Pipeline entrypoint: `uv run mugello06 <stage>`."""

import argparse

from mugello06 import config, ingest, model, publish

STAGES = ("ingest", "model", "publish", "all")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mugello06")
    parser.add_argument("stage", choices=STAGES)
    args = parser.parse_args(argv)
    if args.stage in ("ingest", "all"):
        for path in ingest.run():
            print(f"wrote {path}")
    if args.stage in ("model", "all"):
        print(f"built {config.DUCKDB_PATH}: {', '.join(model.run())}")
    if args.stage in ("publish", "all"):
        print(f"wrote {config.HYPER_PATH}: {', '.join(publish.run())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
