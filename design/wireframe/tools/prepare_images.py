"""Cut the user's local 46 logo out of its white background for previews.

Run: uv run --no-project --with pillow python design/wireframe/tools/prepare_images.py
Reads data/raw/png/ and writes data/interim/images/ (both git-ignored: third-party images).
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw" / "png"
OUT = ROOT / "data" / "interim" / "images"
OUT.mkdir(parents=True, exist_ok=True)

# 46 logo: no white is part of the design, so every near-white pixel becomes transparent
logo = Image.open(RAW / "images.jpg").convert("RGBA")
logo.putdata([  # noqa: getdata is fine for a one-off sketch tool
    (r, g, b, 0) if min(r, g, b) > 225 else (r, g, b, a) for r, g, b, a in logo.getdata()])
logo.crop(logo.getbbox()).save(OUT / "logo46.png")
print("wrote", *sorted(p.name for p in OUT.iterdir()))
