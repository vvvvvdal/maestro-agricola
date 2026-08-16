from __future__ import annotations

import argparse
from pathlib import Path

import qrcode


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "models"
    / "plot_marker"
    / "materials"
    / "textures"
    / "plot-03.png"
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--value", default="plot-03")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image = qrcode.make(args.value)
    image.save(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
