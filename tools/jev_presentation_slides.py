#!/usr/bin/env python3
"""Render slide-ready Jev evidence from the sanitized JEV-42 presentation JSON."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any


LABELS = ("CANCEL", "CONFIRM", "DOCK", "SPRAY", "UNDOCK", "UNKNOWN")
SHORT_LABELS = ("CAN", "CON", "DOC", "SPR", "UND", "UNK")
BACKENDS = ("local", "jev")
WIDTH = 1600
HEIGHT = 900
BG = "#fbfaf5"
INK = "#24311d"
MUTED = "#69745f"
PANEL = "#f1efe4"
GRID = "#d5d2c2"
LOCAL = "#3d6e65"
JEV = "#bb5a24"
YELLOW = "#f5bd24"
RED = "#a43d32"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera SVGs 16:9 da evidencia Jev para slides.")
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def load_evidence(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0" or set(payload.get("backends", {})) != set(BACKENDS):
        raise ValueError("unsupported Jev presentation evidence schema")
    if not isinstance(payload.get("source_metrics_sha256"), str) or len(payload["source_metrics_sha256"]) != 64:
        raise ValueError("missing source metrics sha256")
    for backend in BACKENDS:
        validate_backend(backend, payload["backends"][backend])
    return payload


def validate_backend(name: str, value: Any) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("examples"), int) or value["examples"] <= 0:
        raise ValueError(f"{name}: invalid examples")
    matrix = value.get("confusion_matrix")
    if not isinstance(matrix, dict) or set(matrix) != set(LABELS):
        raise ValueError(f"{name}: invalid matrix rows")
    if any(not isinstance(row, dict) or set(row) != set(LABELS) for row in matrix.values()):
        raise ValueError(f"{name}: invalid matrix columns")
    if not isinstance(value.get("unsafe_accepts"), list):
        raise ValueError(f"{name}: invalid unsafe accepts")


def svg_open(title: str, desc: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{html.escape(title)}</title>',
        f'<desc id="desc">{html.escape(desc)}</desc>',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>',
    ]


def text(x: float, y: float, value: str, size: int, color: str = INK, weight: int = 400, anchor: str = "start") -> str:
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" '
        f'font-family="Arial, sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(value)}</text>'
    )


def footer(evidence: dict[str, Any]) -> list[str]:
    scope = evidence["scope"]
    return [
        f'<line x1="72" y1="820" x2="1528" y2="820" stroke="{GRID}"/>',
        text(72, 852, scope, 20, MUTED),
        text(1528, 852, "Decisao: HOLD - sem adocao operacional", 20, RED, 700, "end"),
        text(72, 878, f"Fonte: JEV-42, SHA-256 {evidence['source_metrics_sha256'][:12]}...", 16, MUTED),
    ]


def header(title_value: str, subtitle: str) -> list[str]:
    return [
        f'<rect x="72" y="60" width="16" height="98" rx="8" fill="{YELLOW}"/>',
        text(116, 100, "MAESTRO AGRICOLA - EXPERIMENTO JEV", 20, MUTED, 700),
        text(116, 146, title_value, 42, INK, 700),
        text(116, 184, subtitle, 21, MUTED),
    ]


def format_decimal(value: float) -> str:
    return f"{value:.4f}".replace(".", ",")


def format_ms(value: float) -> str:
    return f"{value:,.3f}".replace(",", "X").replace(".", ",").replace("X", ".") + " ms"


def format_usd(value: float) -> str:
    return f"US${value:.9f}"


def render_comparison_svg(evidence: dict[str, Any]) -> str:
    local = evidence["backends"]["local"]
    jev = evidence["backends"]["jev"]
    elements = svg_open(
        "Jev versus classificador local - comparacao medida",
        "Comparacao descritiva do corpus sintetico independente. Inclui accuracy, macro-F1, aceitacoes inseguras, latencia e custo.",
    )
    elements.extend(header("Comparacao medida", "Melhor resultado descritivo nao e promocao para o app."))
    elements.extend([
        f'<rect x="72" y="230" width="912" height="530" rx="20" fill="#ffffff" stroke="{GRID}"/>',
        f'<rect x="1010" y="230" width="518" height="530" rx="20" fill="{PANEL}"/>',
        text(116, 276, "METRICA", 19, MUTED, 700),
        text(686, 276, "LOCAL", 19, LOCAL, 700, "middle"),
        text(896, 276, "JEV REMOTO", 19, JEV, 700, "middle"),
    ])
    rows = (
        ("Acertos", f"{local['correct']}/{local['examples']}", f"{jev['correct']}/{jev['examples']}", INK),
        ("Accuracy", format_decimal(local["accuracy"]), format_decimal(jev["accuracy"]), INK),
        ("Macro-F1", format_decimal(local["macro_f1"]), format_decimal(jev["macro_f1"]), INK),
        ("Aceitacoes inseguras", str(len(local["unsafe_accepts"])), str(len(jev["unsafe_accepts"])), RED),
        ("Brier multiclasses", format_decimal(local["calibration"]["brier_multiclass"]), format_decimal(jev["calibration"]["brier_multiclass"]), INK),
        ("Top-label ECE", format_decimal(local["calibration"]["top_label_ece"]), format_decimal(jev["calibration"]["top_label_ece"]), INK),
    )
    for index, (label, local_value, jev_value, label_color) in enumerate(rows):
        y = 328 + index * 68
        if index:
            elements.append(f'<line x1="116" y1="{y - 34}" x2="940" y2="{y - 34}" stroke="{GRID}"/>')
        elements.extend([
            text(116, y, label, 25, label_color, 700 if label_color == RED else 400),
            text(686, y, local_value, 29, LOCAL, 700, "middle"),
            text(896, y, jev_value, 29, JEV, 700, "middle"),
        ])
    elements.extend([
        text(1054, 280, "LATENCIA E CUSTO", 19, MUTED, 700),
        text(1054, 334, "p50", 22, MUTED, 700),
        text(1054, 372, f"Local  {format_ms(local['latency_ms']['p50'])}", 25, LOCAL, 700),
        text(1054, 410, f"Jev     {format_ms(jev['latency_ms']['p50'])}", 25, JEV, 700),
        text(1054, 476, "p95", 22, MUTED, 700),
        text(1054, 514, f"Local  {format_ms(local['latency_ms']['p95'])}", 25, LOCAL, 700),
        text(1054, 552, f"Jev     {format_ms(jev['latency_ms']['p95'])}", 25, JEV, 700),
        text(1054, 618, "Custo total do harness", 22, MUTED, 700),
        text(1054, 656, f"Local  {format_usd(local['cost_usd']['total'])}", 22, LOCAL, 700),
        text(1054, 692, f"Jev     {format_usd(jev['cost_usd']['total'])}", 22, JEV, 700),
        f'<rect x="1038" y="714" width="462" height="54" rx="12" fill="#fce6df"/>',
        text(1064, 748, "Jev: CANCEL -> CONFIRM (0,75)", 21, RED, 700),
    ])
    elements.extend(footer(evidence))
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def cell_fill(row: str, column: str, count: int) -> str:
    if row == column:
        return "#b8d7c4" if count else "#edf2eb"
    if count == 0:
        return "#ffffff"
    if row == "CANCEL" and column == "CONFIRM":
        return "#f5beb8"
    return "#f7dfb0"


def matrix_panel(matrix: dict[str, dict[str, int]], title_value: str, x0: int, color: str) -> list[str]:
    cell, top, left = 64, 370, x0 + 150
    elements = [
        f'<rect x="{x0}" y="250" width="700" height="510" rx="20" fill="#ffffff" stroke="{GRID}"/>',
        text(x0 + 34, 304, title_value, 30, color, 700),
        text(x0 + 34, 332, "linhas: ouro | colunas: predicao", 18, MUTED),
    ]
    for index, label in enumerate(LABELS):
        x = left + index * cell + cell / 2
        y = top + index * cell + cell / 2 + 7
        elements.extend([
            text(x, 360, SHORT_LABELS[index], 15, MUTED, 700, "middle"),
            text(x0 + 134, y, label, 15, MUTED, 700, "end"),
        ])
    for row_index, row in enumerate(LABELS):
        for column_index, column in enumerate(LABELS):
            x = left + column_index * cell
            y = top + row_index * cell
            count = matrix[row][column]
            elements.extend([
                f'<rect x="{x}" y="{y}" width="{cell - 4}" height="{cell - 4}" rx="7" fill="{cell_fill(row, column, count)}" stroke="{GRID}"/>',
                text(x + (cell - 4) / 2, y + (cell - 4) / 2 + 9, str(count), 25, INK, 700, "middle"),
            ])
    return elements


def render_confusion_svg(evidence: dict[str, Any]) -> str:
    local = evidence["backends"]["local"]
    jev = evidence["backends"]["jev"]
    elements = svg_open(
        "Matrizes de confusao Local e Jev",
        "Matrizes de seis rotulos com ouro nas linhas e predicao nas colunas. Erros fora da diagonal sao destacados.",
    )
    elements.extend(header("Onde os classificadores erraram", "Os erros importam mais que um unico numero de accuracy."))
    elements.extend(matrix_panel(local["confusion_matrix"], "Local", 72, LOCAL))
    elements.extend(matrix_panel(jev["confusion_matrix"], "Jev remoto", 828, JEV))
    elements.extend([
        f'<rect x="72" y="776" width="1456" height="38" rx="10" fill="#fce6df"/>',
        text(96, 802, "Aviso de seguranca: Jev teve CANCEL -> CONFIRM (0,75). Local teve 3 aceitacoes inseguras. Nenhuma matriz autoriza movimento.", 19, RED, 700),
    ])
    elements.extend(footer(evidence))
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def reliability_panel(bins: list[dict[str, Any]], title_value: str, color: str, x0: int) -> list[str]:
    panel_w, panel_h, top = 610, 460, 270
    bottom = top + panel_h
    elements = [
        f'<rect x="{x0}" y="220" width="680" height="570" rx="20" fill="#ffffff" stroke="{GRID}"/>',
        text(x0 + 36, 272, title_value, 30, color, 700),
        f'<rect x="{x0 + 58}" y="{top}" width="{panel_w}" height="{panel_h}" fill="#fbfaf5" stroke="{MUTED}"/>',
        f'<line x1="{x0 + 58}" y1="{bottom}" x2="{x0 + 58 + panel_w}" y2="{top}" stroke="{MUTED}" stroke-dasharray="10 8" stroke-width="2"/>',
    ]
    for tick in (0.0, 0.5, 1.0):
        x = x0 + 58 + tick * panel_w
        y = bottom - tick * panel_h
        elements.extend([
            text(x, bottom + 32, f"{tick:.1f}", 18, MUTED, 400, "middle"),
            text(x0 + 42, y + 7, f"{tick:.1f}", 18, MUTED, 400, "end"),
        ])
    for index, bin_ in enumerate(bins):
        confidence = float(bin_["confidence"])
        accuracy = float(bin_["accuracy"])
        x = x0 + 58 + confidence * panel_w
        y = bottom - accuracy * panel_h
        radius = 12 + min(16, int(bin_["examples"]) // 2)
        label_offset = 18 if index % 2 else 42
        elements.extend([
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{color}" fill-opacity="0.84" stroke="{INK}" stroke-width="1.5"/>',
            text(x, y - label_offset, f"n={bin_['examples']}", 18, INK, 700, "middle"),
        ])
    elements.extend([
        text(x0 + 363, 768, "confianca media", 19, MUTED, 400, "middle"),
        (
            f'<text x="{x0 + 18}" y="500" text-anchor="middle" '
            f'transform="rotate(-90 {x0 + 18} 500)" font-family="Arial, sans-serif" '
            f'font-size="19" fill="{MUTED}">accuracy observada</text>'
        ),
    ])
    return elements


def render_reliability_svg(evidence: dict[str, Any]) -> str:
    local = evidence["backends"]["local"]
    jev = evidence["backends"]["jev"]
    elements = svg_open(
        "Reliability diagram Local e Jev",
        "Confianca media no eixo horizontal e accuracy observada no vertical, com bins ocupados identificados por tamanho amostral.",
    )
    elements.extend(header("Reliability diagram", "Leitura descritiva: este grafico nao prova calibracao geral nem seguranca."))
    elements.extend(reliability_panel(local["calibration"]["occupied_bins"], "Local", LOCAL, 72))
    elements.extend(reliability_panel(jev["calibration"]["occupied_bins"], "Jev remoto", JEV, 848))
    elements.extend([
        f'<rect x="72" y="792" width="1456" height="28" rx="8" fill="#fce6df"/>',
        text(96, 813, "Diagonal tracejada = calibracao ideal. Jev ainda teve CANCEL -> CONFIRM; nao usar o grafico como selo de seguranca.", 18, RED, 700),
    ])
    elements.extend(footer(evidence))
    elements.append("</svg>")
    return "\n".join(elements) + "\n"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_slide_assets(evidence_path: Path, output_dir: Path) -> dict[str, Path]:
    evidence = load_evidence(evidence_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "comparison": output_dir / "jev-final-recovery-comparison-slide.svg",
        "confusion": output_dir / "jev-final-recovery-confusion-slide.svg",
        "reliability": output_dir / "jev-final-recovery-reliability-slide.svg",
    }
    renderers = {
        "comparison": render_comparison_svg,
        "confusion": render_confusion_svg,
        "reliability": render_reliability_svg,
    }
    for name, path in paths.items():
        content = renderers[name](evidence)
        path.write_text(content, encoding="utf-8")
    return paths


def main() -> None:
    args = parse_args()
    paths = write_slide_assets(args.evidence, args.output_dir)
    print(f"wrote {len(paths)} Jev slide assets to {args.output_dir}")


if __name__ == "__main__":
    main()
