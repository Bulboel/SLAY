"""Prepare browser-safe backgrounds and repair pale sprite alpha for V0.0.8."""

from pathlib import Path
import sys
from collections import deque

from PIL import Image, ImageEnhance, ImageFilter, ImageOps


def browser_safe_rgba(source: Path, target: Path) -> None:
    image = Image.open(source).convert("RGBA")
    image.save(target, "PNG", compress_level=6)


def recolor_building(source: Path, target: Path, hue_shift: int) -> None:
    image = Image.open(source).convert("RGBA")
    rgb = image.convert("RGB")
    hsv = rgb.convert("HSV")
    h, s, v = hsv.split()
    h = h.point(lambda value: (value + hue_shift) % 256)
    recolored = Image.merge("HSV", (h, s, v)).convert("RGB")
    recolored = ImageEnhance.Color(recolored).enhance(1.12)
    recolored.putalpha(image.getchannel("A"))
    recolored.save(target, "PNG", compress_level=6)


def fill_alpha_holes(source: Path, target: Path, cream=(238, 222, 211)) -> None:
    """Fill transparent holes enclosed by the visible creature silhouette."""
    image = Image.open(source).convert("RGBA")
    px = image.load()
    width, height = image.size
    seen = bytearray(width * height)
    queue = deque()
    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(1, height - 1):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        index = y * width + x
        if seen[index]:
            continue
        seen[index] = 1
        r, g, b, a = px[x, y]
        is_background = a < 28 or (max(r, g, b) - min(r, g, b) < 25 and min(r, g, b) > 175)
        if not is_background:
            continue
        px[x, y] = (r, g, b, 0)
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))

    alpha = image.getchannel("A")
    opaque = alpha.point(lambda value: 255 if value >= 28 else 0)
    # A modest close joins pale body regions that were eaten by old background removal.
    closed = opaque.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
    mask = closed.load()
    for y in range(image.height):
        for x in range(image.width):
            if mask[x, y] and px[x, y][3] < 28:
                px[x, y] = (*cream, 255)
    image.putalpha(ImageOps.autocontrast(image.getchannel("A")))
    image.save(target, "PNG", compress_level=6)


def make_jpeg(source: Path, target: Path, size: tuple[int, int]) -> None:
    image = Image.open(source).convert("RGB")
    image = ImageOps.fit(image, size, Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    image.save(target, "JPEG", quality=92, subsampling=0, optimize=True)


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: repair-v008-assets.py VILLAGE_SOURCE BEACH_SOURCE THEATER_SOURCE ASSET_DIR")
    village_source, beach_source, theater_source, asset_dir = map(Path, sys.argv[1:])
    asset_dir.mkdir(parents=True, exist_ok=True)
    make_jpeg(village_source, asset_dir / "bitch-city-ground-v1.jpg", (960, 768))
    make_jpeg(beach_source, asset_dir / "beach-background-v1.jpg", (960, 704))
    make_jpeg(theater_source, asset_dir / "slayhouse-interior-v1.jpg", (640, 480))
    recolor_building(asset_dir / "house-pink-v1.png", asset_dir / "house-teal-v1.png", 78)
    recolor_building(asset_dir / "slayhouse-v1.png", asset_dir / "slayhouse-teal-v1.png", 74)
    browser_safe_rgba(asset_dir / "sexyflex-pose-v1.png", asset_dir / "sexyflex-pose-v2.png")
    for name in ("normal", "attack", "hit", "down"):
        fill_alpha_holes(asset_dir / f"veloursa-{name}-v1.png", asset_dir / f"veloursa-{name}-v2.png")
    fill_alpha_holes(asset_dir / "veloursa-map-v3.png", asset_dir / "veloursa-map-v4.png")
    fill_alpha_holes(asset_dir / "sexyflex-map-v3.png", asset_dir / "sexyflex-map-v4.png", (232, 219, 198))
    print("V0.0.8 assets prepared")
