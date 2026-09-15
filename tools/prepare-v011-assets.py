from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SPEC = spec_from_file_location("prepare_v010", ROOT / "tools" / "prepare-v010-assets.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load the shared sprite preparation helper")
HELPER = module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit("usage: prepare-v011-assets.py DANTONLIX VELOURQUINE")
    HELPER.extract_character(sys.argv[1], "dantonlix-map-v3.png", remove_enclosed_checker=True)
    HELPER.extract_character(sys.argv[2], "velourquine-map-v1.png")


if __name__ == "__main__":
    main()
