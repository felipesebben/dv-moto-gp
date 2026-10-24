"""Cut the user's local helmet + 46 logo images out of their white backgrounds for previews.

Run: uv run --no-project --with pillow python design/wireframe/tools/prepare_images.py
Reads data/raw/png/ and writes data/interim/images/ (both git-ignored: third-party images).
"""

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "png"
OUT = ROOT / "data" / "interim" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# helmet: the photo shows four views; keep the side view with the sun and the AGV logo, and
# clear only the white that touches the border (the helmet itself is white, so a plain
# threshold would eat it)
helmet = Image.open(RAW / "718150ade32994e8f8a1dac90da42b38.jpg").convert("RGBA").crop((242, 2, 472, 238))
w, h = helmet.size
for xy in [(x, 0) for x in range(0, w, 6)] + [(x, h - 1) for x in range(0, w, 6)] + \
          [(0, y) for y in range(0, h, 6)] + [(w - 1, y) for y in range(0, h, 6)]:
    if helmet.getpixel(xy)[3] and min(helmet.getpixel(xy)[:3]) > 225:
        ImageDraw.floodfill(helmet, xy, (0, 0, 0, 0), thresh=40)
helmet.crop(helmet.getbbox()).save(OUT / "helmet.png")

# 46 logo: no white is part of the design, so every near-white pixel becomes transparent
logo = Image.open(RAW / "images.jpg").convert("RGBA")
logo.putdata([  # noqa: getdata is fine for a one-off sketch tool
    (r, g, b, 0) if min(r, g, b) > 225 else (r, g, b, a) for r, g, b, a in logo.getdata()])
logo.crop(logo.getbbox()).save(OUT / "logo46.png")
print("wrote", *sorted(p.name for p in OUT.iterdir()))
