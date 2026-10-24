"""Low-level helpers to turn Tissot timing PDFs into text lines."""

import re
from pathlib import Path

import pdfplumber

LAP_TIME = r"\d+'\d{2}\.\d{3}"


def to_seconds(lap_time: str) -> float:
    """Convert a Tissot time like "1'50.195" or "42'39.610" to seconds."""
    minutes, seconds = lap_time.split("'")
    return int(minutes) * 60 + float(seconds)


def lines(path: Path) -> list[str]:
    """All text lines of a single-column PDF, page by page."""
    with pdfplumber.open(path) as pdf:
        return [ln for page in pdf.pages for ln in (page.extract_text() or "").splitlines()]


def column_lines(path: Path) -> list[str]:
    """Text lines of a two-column PDF, read left column then right column per page.

    The gutter is placed halfway between the left column's "Speed" header and the
    right column's first "Lap" header, so long values never get cut in half.
    """
    out: list[str] = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            words = page.extract_words()
            speed_end = next(w["x1"] for w in words if w["text"] == "Speed")
            right_start = min(w["x0"] for w in words if w["text"] == "Lap" and w["x0"] > speed_end)
            gutter = (speed_end + right_start) / 2
            for box in ((0, 0, gutter, page.height), (gutter, 0, page.width, page.height)):
                out.extend((page.crop(box).extract_text() or "").splitlines())
    return out


def strip_ws(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()
