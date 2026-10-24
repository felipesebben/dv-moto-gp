"""Pure line parsers for each Tissot report. Each returns a polars DataFrame."""

import re

import polars as pl

from mugello06.ingest.pdf_text import LAP_TIME, strip_ws, to_seconds

_CLASSIFIED = re.compile(
    rf"^(?P<position>\d+) (?:(?P<points>\d+) )?(?P<number>\d+) "
    rf"(?P<name>.+?) (?P<nation>[A-Z]{{3}}) (?P<team>.+) (?P<motorcycle>\S+) "
    rf"(?P<total_time>{LAP_TIME}) (?P<avg_kmh>\d+\.\d+)(?: (?P<gap>.+))?$"
)
_NOT_CLASSIFIED = re.compile(
    rf"^(?P<number>\d+) (?P<name>.+?) (?P<nation>[A-Z]{{3}}) (?P<team>.+) (?P<motorcycle>\S+) "
    rf"(?P<total_time>{LAP_TIME}) (?P<avg_kmh>\d+\.\d+) (?P<laps_down>\d+) laps?$"
)


def _split_name(name: str) -> tuple[str, str]:
    """'Kenny ROBERTS JR' -> ('Kenny', 'ROBERTS JR'): the surname is the upper-case tail."""
    tokens = name.split()
    first = [t for t in tokens if not t.isupper()]
    last = [t for t in tokens if t.isupper()]
    return " ".join(first), " ".join(last)


def parse_classification(lines: list[str], race_laps: int) -> pl.DataFrame:
    rows = []
    classified = True
    for raw in lines:
        line = strip_ws(raw)
        if line == "Not Classified":
            classified = False
            continue
        m = (_CLASSIFIED if classified else _NOT_CLASSIFIED).match(line)
        if not m:
            continue
        d = m.groupdict()
        first, last = _split_name(d["name"])
        gap = d.get("gap")
        laps_down = int(d["laps_down"]) if d.get("laps_down") else 0
        if gap and gap.endswith(("lap", "laps")):
            laps_down, gap = int(gap.split()[0]), None
        rows.append(
            {
                "rider_number": int(d["number"]),
                "first_name": first,
                "surname": last,
                "nation": d["nation"],
                "team": d["team"],
                "motorcycle": d["motorcycle"],
                "status": "classified" if classified else "dnf",
                "position": int(d["position"]) if classified else None,
                "points": int(d["points"]) if d.get("points") else 0,
                "laps_completed": race_laps - laps_down,
                "total_time_s": to_seconds(d["total_time"]),
                "avg_kmh": float(d["avg_kmh"]),
                "gap_s": to_seconds(gap) if gap and "'" in gap else float(gap) if gap else None,
            }
        )
    return pl.DataFrame(rows)


_LAP_ROW = re.compile(r"^(?:Grid|(?:[Laps] )?(\d+))((?: \d+)+)$")


def parse_lap_chart(lines: list[str]) -> pl.DataFrame:
    """Long table of (lap, position, rider_number); lap 0 is the starting grid."""
    rows = []
    for raw in lines:
        line = strip_ws(raw)
        m = _LAP_ROW.match(line)
        if not m or line.startswith("Pos"):
            continue
        lap = int(m.group(1)) if m.group(1) else 0
        for position, number in enumerate(m.group(2).split(), start=1):
            rows.append({"lap": lap, "position": position, "rider_number": int(number)})
    return pl.DataFrame(rows)


_RIDER_HEADER = re.compile(r"^\d+(?:st|nd|rd|th) (\d+)\b")
_SECTOR = r"(\d+\.\d{3})"
_ANALYSIS_ROW = re.compile(
    rf"^(\d+) (P )?({LAP_TIME}) {_SECTOR} {_SECTOR} {_SECTOR} {_SECTOR}(?: (\d+\.\d))?$"
)


def parse_analysis(lines: list[str]) -> pl.DataFrame:
    """One row per rider per completed lap, with the four sector times and speed-trap km/h."""
    rows = []
    rider: int | None = None
    for raw in lines:
        line = strip_ws(raw)
        if h := _RIDER_HEADER.match(line):
            rider = int(h.group(1))
            continue
        m = _ANALYSIS_ROW.match(line)
        if not m or rider is None:
            continue
        lap, pit, lap_time, t1, t2, t3, t4, speed = m.groups()
        rows.append(
            {
                "rider_number": rider,
                "lap": int(lap),
                "lap_time_s": to_seconds(lap_time),
                "t1_s": float(t1),
                "t2_s": float(t2),
                "t3_s": float(t3),
                "t4_s": float(t4),
                "speed_kmh": float(speed) if speed else None,
                "pit_lane": pit is not None,
            }
        )
    return pl.DataFrame(rows)
