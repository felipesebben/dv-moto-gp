import pytest

from mugello06.ingest import parsers, race_laps
from mugello06.ingest.pdf_text import to_seconds

CLASSIFICATION = """\
Classification after 23 laps = 120.635 km 20
Pos Rider Nation Team Motorcycle Total Time Km/h Gap
1 25 46 Valentino ROSSI ITA Camel Yamaha Team YAMAHA 42'39.610 169.668
8 8 10 Kenny ROBERTS JR USA Team Roberts KR211V 42'58.782 168.407 19.172
16 77 James ELLISON GBR Tech 3 Yamaha YAMAHA 43'52.997 164.939 1'13.387
17 30 Jose Luis CARDOSO SPA Pramac d'Antín MotoGP DUCATI 42'45.597 161.913 1 lap
Not Classified
27 Casey STONER AUS Honda LCR HONDA 14'52.930 169.168 15 laps
Race condition:Dry Pole Position: Sete GIBERNAU 1'48.969 173.278 Km/h
""".splitlines()


@pytest.mark.parametrize(
    ("raw", "seconds"), [("1'50.195", 110.195), ("42'39.610", 2559.61), ("0'00.575", 0.575)]
)
def test_to_seconds(raw: str, seconds: float) -> None:
    assert to_seconds(raw) == pytest.approx(seconds)


def test_race_laps() -> None:
    assert race_laps(CLASSIFICATION) == 23


def test_classification() -> None:
    df = parsers.parse_classification(CLASSIFICATION, race_laps=23)
    rows = {r["rider_number"]: r for r in df.iter_rows(named=True)}

    assert set(rows) == {46, 10, 77, 30, 27}
    assert rows[46]["position"] == 1 and rows[46]["points"] == 25 and rows[46]["gap_s"] is None
    assert (rows[10]["first_name"], rows[10]["surname"], rows[10]["motorcycle"]) == (
        "Kenny",
        "ROBERTS JR",
        "KR211V",
    )
    assert rows[77]["points"] == 0 and rows[77]["gap_s"] == pytest.approx(73.387)
    assert rows[30]["first_name"] == "Jose Luis" and rows[30]["laps_completed"] == 22
    assert rows[27]["status"] == "dnf" and rows[27]["laps_completed"] == 8
    assert rows[27]["position"] is None


def test_lap_chart_reads_grid_and_vertical_label_rows() -> None:
    df = parsers.parse_lap_chart(
        ["Pos 1 2 3", "Grid 15 65 46", "L 11 46 15 69", "s", "23 46 65 69", "Lap Chart 22"]
    )
    assert df["lap"].unique().sort().to_list() == [0, 11, 23]
    grid = df.filter(df["lap"] == 0).sort("position")["rider_number"].to_list()
    assert grid == [15, 65, 46]


def test_analysis_assigns_laps_to_current_rider() -> None:
    df = parsers.parse_analysis(
        [
            "1st 46 Valentino ROSSI ITA",
            "1 1'56.718 31.908 23.451 36.034 25.325",
            "2 1'50.868 25.784 23.226 36.304 25.554 321.6",
            "2nd 65",
            "7 P 1'50.195 25.964 23.356 35.888 24.987 323.7",
            "unfinished 25.828 23.482 329.3",
            "Fastest Lap 1'50.357 25.949 23.144 35.974 25.290",
        ]
    )
    assert df.select("rider_number", "lap").rows() == [(46, 1), (46, 2), (65, 7)]
    assert df["speed_kmh"].to_list() == [None, 321.6, 323.7]
    assert df["pit_lane"].to_list() == [False, False, True]
