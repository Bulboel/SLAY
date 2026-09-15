from collections import deque
from pathlib import Path
import sys

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"


def extract_character(source: str, target: str = "sexyflex-map-v5.png", remove_enclosed_checker: bool = False) -> None:
    image = Image.open(source).convert("RGBA")
    width, height = image.size
    pixels = image.load()

    # The generator sometimes previews transparency as a baked neutral-grey grid.
    # Flood-fill only neutral background tones connected to the canvas border so
    # pale fur and costume details inside the outlined character stay intact.
    candidate = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            neutral = max(r, g, b) - min(r, g, b) < 22
            middle_grey = 65 < (r + g + b) / 3
            if a < 8 or (neutral and middle_grey):
                candidate[y * width + x] = 1

    outside = bytearray(width * height)
    queue = deque()
    for x in range(width):
        queue.extend((x, (height - 1) * width + x))
    for y in range(height):
        queue.extend((y * width, y * width + width - 1))
    while queue:
        index = queue.popleft()
        if outside[index] or not candidate[index]:
            continue
        outside[index] = 1
        x, y = index % width, index // width
        for ny in range(max(0, y - 1), min(height, y + 2)):
            for nx in range(max(0, x - 1), min(width, x + 2)):
                neighbor = ny * width + nx
                if not outside[neighbor] and candidate[neighbor]:
                    queue.append(neighbor)

    for y in range(height):
        for x in range(width):
            r, g, b, _ = pixels[x, y]
            enclosed_checker = remove_enclosed_checker and max(r, g, b) - min(r, g, b) < 22 and (r + g + b) / 3 > 170
            if outside[y * width + x] or enclosed_checker:
                pixels[x, y] = (r, g, b, 0)

    bbox = image.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("Sexyflex extraction produced an empty image")
    image = image.crop(bbox)
    image.thumbnail((512, 512), Image.Resampling.LANCZOS)
    image.save(ASSETS / target, "PNG", optimize=True)


def crop_nicky() -> None:
    source = Image.open(ASSETS / "portrait-nicky-v1.png").convert("RGBA")
    # Remove the title panel on the left while retaining her crown, face, bow,
    # torso and lower costume. Padding keeps the portrait undistorted in its box.
    crop = source.crop((160, 0, 512, 352))
    crop = crop.resize((512, 512), Image.Resampling.LANCZOS)
    crop.save(ASSETS / "portrait-nicky-v2.png", "PNG", optimize=True)


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: prepare-v010-assets.py GENERATED_SEXYFLEX")
    extract_character(sys.argv[1])
    crop_nicky()


if __name__ == "__main__":
    main()
