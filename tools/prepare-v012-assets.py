from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "dist" / "assets"
SPEC = spec_from_file_location("prepare_v010", ROOT / "tools" / "prepare-v010-assets.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load the shared sprite preparation helper")
HELPER = module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
COMPONENT_SPEC = spec_from_file_location("prepare_v009", ROOT / "tools" / "prepare-v009-assets.py")
if COMPONENT_SPEC is None or COMPONENT_SPEC.loader is None:
    raise RuntimeError("Unable to load the alpha-component helper")
COMPONENT_HELPER = module_from_spec(COMPONENT_SPEC)
COMPONENT_SPEC.loader.exec_module(COMPONENT_HELPER)


def prepare_route(source: str) -> None:
    image = Image.open(source).convert("RGB")
    image = ImageOps.fit(image, (832, 1280), method=Image.Resampling.LANCZOS)
    image.save(ASSETS / "route-28-v1.jpg", "JPEG", quality=91, optimize=True, progressive=True)


def prepare_jason(source: str) -> None:
    character = Image.open(source).convert("RGBA")
    pixels = character.load()
    for y in range(character.height):
        for x in range(character.width):
            r, g, b, _ = pixels[x, y]
            dominance = g - max(r, b)
            if g > 125 and dominance > 20:
                alpha = max(0, min(255, round(255 * (80 - dominance) / 60)))
                g = min(g, max(r, b) + 4)
                pixels[x, y] = (r, g, b, alpha)
            elif g > 80 and dominance > 5:
                pixels[x, y] = (r, max(r, b) + 4, b, 255)
    bbox = character.getchannel("A").getbbox()
    if not bbox:
        raise RuntimeError("Jason chroma-key extraction produced an empty image")
    character = character.crop(bbox)
    character.thumbnail((512, 512), Image.Resampling.LANCZOS)
    character.save(ASSETS / "jason-map-v1.png", "PNG", optimize=True)
    side = min(character.width, int(character.height * 0.58))
    left = max(0, (character.width - side) // 2)
    portrait = character.crop((left, 0, left + side, side))
    portrait = portrait.resize((512, 512), Image.Resampling.LANCZOS)
    portrait.save(ASSETS / "portrait-jason-v1.png", "PNG", optimize=True)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare-v012-assets.py ROUTE JASON")
    prepare_route(sys.argv[1])
    prepare_jason(sys.argv[2])


if __name__ == "__main__":
    main()
