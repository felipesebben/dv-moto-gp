"""Make the custom Tableau shapes: the numbered badges, the rider dots and the Mugello marker.

Run: uv run python design/tableau/tools/make_shapes.py
Writes design/tableau/shapes/Mugello 2006/*.png, and a contact sheet with every shape and its
name at design/tableau/previews/shapes.png. Copy the folder into
Documents/My Tableau Repository/Shapes/ (docs/TABLEAU_GUIDE.md, §2.2).

Why images: Tableau colours a shape mark with one colour and draws no border on it, so a
yellow badge with a dark ring and a dark number can't be built from a circle mark. Each PNG
carries its own fill, ring and number. The file names are the values of the `shape_file` column
in the .hyper (macro `shape_name` in sql/00_macros.sql). Proportions follow the wireframe
(design/wireframe/tools/sketchlib.py `badge()` and build_poster_d.py): the circle fills the
square image, so Tableau's size slider sets the outer diameter.

The digits are Barlow Condensed Bold (SIL Open Font License), downloaded from the Google Fonts
repository the first time the script runs.
"""

import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "design" / "tableau" / "shapes" / "Mugello 2006"
FONT_URL = "https://github.com/google/fonts/raw/main/ofl/barlowcondensed/BarlowCondensed-Bold.ttf"
FONT = ROOT / "data" / "interim" / "BarlowCondensed-Bold.ttf"  # git-ignored cache
C = {"bg": "#1C1A19", "ink": "#F2EFE9", "protagonist": "#FDF504", "rival": "#F26B5B"}
SIZE = 512  # px per side; printed, a 26 px badge is about 1.6 cm, so this is well over 600 dpi
SS = 4  # drawn at 4x and scaled down, for smooth edges


def circle(draw: ImageDraw.ImageDraw, r: float, fill: str) -> None:
    c = SIZE * SS / 2
    draw.ellipse((c - r, c - r, c + r, c + r), fill=fill)


def shape(layers: list[tuple[float, str]], digit: str = "", ink: str = "", digit_h: float = 0) -> Image.Image:
    """Concentric discs, given as (radius as a share of the outer radius, colour), outer first."""
    img = Image.new("RGBA", (SIZE * SS, SIZE * SS), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    outer = SIZE * SS / 2 - SS  # a pixel of margin so the edge isn't clipped
    for share, colour in layers:
        circle(draw, outer * share, colour)
    if digit:
        # size the font by the digit's own height, then centre the ink (not the text box)
        font = ImageFont.truetype(str(FONT), 100)
        top, bottom = font.getbbox("0")[1], font.getbbox("0")[3]
        font = ImageFont.truetype(str(FONT), round(100 * outer * 2 * digit_h / (bottom - top)))
        x0, y0, x1, y1 = draw.textbbox((0, 0), digit, font=font)
        c = SIZE * SS / 2
        draw.text((c - (x0 + x1) / 2, c - (y0 + y1) / 2), digit, font=font, fill=ink)
    return img.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def main() -> None:
    if not FONT.exists():
        FONT.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(FONT_URL, FONT)
    OUT.mkdir(parents=True, exist_ok=True)
    # badge: r 12 + a 2 px ring centred on the edge, so 26 px across with a ring from r 11 to 13;
    # the digit is 12.6 px type, whose figures stand about 0.7 of that, so ~0.34 of the diameter
    ring, digit_h = 11 / 13, 0.34
    shapes = {}
    for n in range(1, 8):
        shapes[f"badge_protagonist_{n}"] = shape(
            [(1, C["bg"]), (ring, C["protagonist"])], str(n), C["bg"], digit_h)
        shapes[f"badge_rival_{n}"] = shape([(1, C["rival"]), (ring, C["bg"])], str(n), C["ink"], digit_h)
    # rider dot: r 5 + a 2 px dark ring, 12 px across
    for role in ("protagonist", "rival"):
        shapes[f"dot_{role}"] = shape([(1, C["bg"]), (4 / 6, C[role])])
    # Mugello marker: a yellow ring r 9 (stroke 2, so 8 to 10) around a yellow dot r 3.5, 20 px
    shapes["mugello_marker"] = shape(
        [(1, C["protagonist"]), (8 / 10, (0, 0, 0, 0)), (3.5 / 10, C["protagonist"])])  # type: ignore[list-item]
    for name, img in shapes.items():
        img.save(OUT / f"{name}.png")
    print(f"wrote {len(shapes)} shapes to {OUT}")
    contact_sheet(shapes)


def contact_sheet(shapes: dict[str, Image.Image]) -> None:
    """Every shape at 96 px on the poster background, with its file name under it."""
    cols, cell = 7, (176, 148)
    rows = -(-len(shapes) // cols)
    sheet = Image.new("RGB", (cols * cell[0], rows * cell[1]), C["bg"])
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(str(FONT), 17)
    for i, (name, img) in enumerate(shapes.items()):
        x, y = i % cols * cell[0], i // cols * cell[1]
        sheet.paste(img.resize((96, 96), Image.Resampling.LANCZOS), (x + 40, y + 12),
                    img.resize((96, 96), Image.Resampling.LANCZOS))
        draw.text((x + cell[0] / 2, y + 128), name, font=font, fill=C["ink"], anchor="mm")
    path = ROOT / "design" / "tableau" / "previews" / "shapes.png"
    sheet.save(path)
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
