from __future__ import annotations

import argparse
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
TEXTURE_DIR = (
    ROOT
    / "robot_ws"
    / "src"
    / "maestro_simulation"
    / "models"
    / "plot_marker"
    / "materials"
    / "textures"
)
DEFAULT_OUTPUT = TEXTURE_DIR / "plot-03.png"
DEFAULT_QR_OUTPUT = TEXTURE_DIR / "plot-03-qr.png"


def _opencv():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError as exc:
        raise RuntimeError("OpenCV e NumPy são necessários para gerar a placa") from exc
    if not hasattr(cv2, "QRCodeEncoder_create"):
        raise RuntimeError("esta versão do OpenCV não possui QRCodeEncoder_create")
    return cv2, np


def centered_text(cv2, image, text: str, y: int, scale: float, color, thickness: int) -> None:
    font = cv2.FONT_HERSHEY_DUPLEX
    width = cv2.getTextSize(text, font, scale, thickness)[0][0]
    cv2.putText(image, text, ((image.shape[1] - width) // 2, y), font, scale, color, thickness, cv2.LINE_AA)


def build_marker(value: str):
    cv2, np = _opencv()
    qr = cv2.QRCodeEncoder_create().encode(value)
    raw_qr = cv2.resize(qr, (290, 290), interpolation=cv2.INTER_NEAREST)

    marker = np.full((960, 720, 3), 255, dtype=np.uint8)
    marker[:180, :] = (56, 92, 38)
    centered_text(cv2, marker, value.upper(), 120, 2.2, (255, 255, 255), 5)

    display_qr = cv2.resize(qr, (540, 540), interpolation=cv2.INTER_NEAREST)
    marker[230:770, 90:630] = cv2.cvtColor(display_qr, cv2.COLOR_GRAY2BGR)
    centered_text(cv2, marker, "ALVO MAPEADO", 865, 1.05, (34, 52, 28), 3)
    centered_text(cv2, marker, "MAESTRO AGRICOLA", 920, 0.75, (76, 92, 72), 2)
    cv2.rectangle(marker, (8, 8), (711, 951), (34, 52, 28), 8)
    return raw_qr, marker


def main() -> int:
    parser = argparse.ArgumentParser(description="Gera o QR e a placa humana/máquina do talhão")
    parser.add_argument("--value", default="plot-03")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--qr-output", type=Path, default=DEFAULT_QR_OUTPUT)
    args = parser.parse_args()
    try:
        cv2, _ = _opencv()
        raw_qr, marker = build_marker(args.value)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.qr_output.parent.mkdir(parents=True, exist_ok=True)
        if not cv2.imwrite(str(args.qr_output), raw_qr) or not cv2.imwrite(str(args.output), marker):
            raise RuntimeError("falha ao gravar as imagens")
    except (OSError, RuntimeError) as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 1
    print(args.output)
    print(args.qr_output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
