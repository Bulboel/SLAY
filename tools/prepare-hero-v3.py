"""Prepare browser-safe V0.0.7 hero and interior PNG assets."""

from pathlib import Path
import sys

from PIL import Image


def clean_hero(source_path: Path, output_path: Path) -> None:
    source = Image.open(source_path).convert("RGB")
    cell_width = source.width // 8
    sheet = Image.new("RGBA", (8 * 64, 80), (0, 0, 0, 0))

    for index in range(8):
        left = index * cell_width
        right = source.width if index == 7 else (index + 1) * cell_width
        frame = source.crop((left, 0, right, source.height)).convert("RGBA")
        pixels = frame.load()
        for y in range(frame.height):
            for x in range(frame.width):
                r, g, b, _ = pixels[x, y]
                # The generated preview uses a neutral checkerboard instead of alpha.
                # Remove only bright, nearly neutral pixels so the dark outline survives.
                if max(r, g, b) - min(r, g, b) < 18 and min(r, g, b) > 118:
                    pixels[x, y] = (r, g, b, 0)

        bounds = frame.getbbox()
        if not bounds:
            raise RuntimeError(f"Hero frame {index} is empty")
        frame = frame.crop(bounds)

        # Deliberately simplify to a stable pixel grid before scaling back up.
        scale = min(26 / frame.width, 36 / frame.height)
        tiny_size = (max(1, round(frame.width * scale)), max(1, round(frame.height * scale)))
        tiny = frame.resize(tiny_size, Image.Resampling.NEAREST)
        rendered = tiny.resize((tiny.width * 2, tiny.height * 2), Image.Resampling.NEAREST)
        x = index * 64 + (64 - rendered.width) // 2
        y = 76 - rendered.height
        sheet.alpha_composite(rendered, (x, y))

    sheet.save(output_path, format="PNG", compress_level=6)


def clean_interior(source_path: Path, output_path: Path) -> None:
    # RGB output avoids the partial alpha decode seen in Chromium on the old file.
    interior = Image.open(source_path).convert("RGB").resize((640, 480), Image.Resampling.LANCZOS)
    interior.save(output_path, format="PNG", compress_level=6)


def validate(path: Path, size: tuple[int, int], alpha_required: bool) -> None:
    image = Image.open(path)
    image.load()
    if image.size != size:
        raise RuntimeError(f"{path.name}: {image.size}, expected {size}")
    if alpha_required and image.mode != "RGBA":
        raise RuntimeError(f"{path.name}: transparent RGBA output required")
    if not alpha_required and image.mode != "RGB":
        raise RuntimeError(f"{path.name}: browser-safe RGB output required")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise SystemExit("usage: prepare-hero-v3.py HERO_SOURCE INTERIOR_SOURCE ASSET_DIR")
    hero_source = Path(sys.argv[1])
    interior_source = Path(sys.argv[2])
    asset_dir = Path(sys.argv[3])
    asset_dir.mkdir(parents=True, exist_ok=True)
    hero_output = asset_dir / "hero-map-v3.png"
    interior_output = asset_dir / "home-interior-v2.png"
    clean_hero(hero_source, hero_output)
    clean_interior(interior_source, interior_output)
    validate(hero_output, (512, 80), True)
    validate(interior_output, (640, 480), False)
    print(f"OK {hero_output.name} 512x80 RGBA")
    print(f"OK {interior_output.name} 640x480 RGB")
