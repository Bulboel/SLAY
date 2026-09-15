from collections import deque
from pathlib import Path
import sys

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"


def fit_jpeg(source: str, target: str, size: tuple[int, int]) -> None:
    image = Image.open(source).convert("RGB")
    image = ImageOps.fit(image, size, method=Image.Resampling.LANCZOS)
    image.save(ASSETS / target, "JPEG", quality=91, optimize=True, progressive=True)


def keep_largest_alpha_component(source: str, target: str) -> None:
    image = Image.open(ASSETS / source).convert("RGBA")
    alpha = image.getchannel("A")
    width, height = image.size
    pixels = alpha.load()
    active = bytearray(width * height)
    for y in range(height):
        for x in range(width):
            if pixels[x, y] >= 18:
                active[y * width + x] = 1

    seen = bytearray(width * height)
    largest: list[int] = []
    for start in range(width * height):
        if not active[start] or seen[start]:
            continue
        component: list[int] = []
        queue = deque([start])
        seen[start] = 1
        while queue:
            index = queue.popleft()
            component.append(index)
            x, y = index % width, index // width
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    neighbor = ny * width + nx
                    if active[neighbor] and not seen[neighbor]:
                        seen[neighbor] = 1
                        queue.append(neighbor)
        if len(component) > len(largest):
            largest = component

    keep = bytearray(width * height)
    for index in largest:
        keep[index] = 1
    rgba = image.load()
    for y in range(height):
        for x in range(width):
            if not keep[y * width + x]:
                r, g, b, _ = rgba[x, y]
                rgba[x, y] = (r, g, b, 0)
    image.save(ASSETS / target, "PNG", optimize=True)


def main() -> None:
    if len(sys.argv) != 4:
        raise SystemExit("usage: prepare-v009-assets.py VILLAGE WEST EAST")
    fit_jpeg(sys.argv[1], "bitch-city-v2.jpg", (960, 768))
    fit_jpeg(sys.argv[2], "west-festival-v1.jpg", (960, 704))
    fit_jpeg(sys.argv[3], "east-park-v1.jpg", (960, 704))
    for source, target in (
        ("sexyflex-attack-v4.png", "sexyflex-attack-v5.png"),
        ("sexyflex-hit-v4.png", "sexyflex-hit-v5.png"),
        ("sexyflex-down-v4.png", "sexyflex-down-v5.png"),
        ("dantonlix-hit-v4.png", "dantonlix-hit-v5.png"),
        ("dantonlix-down-v4.png", "dantonlix-down-v5.png"),
    ):
        keep_largest_alpha_component(source, target)


if __name__ == "__main__":
    main()
