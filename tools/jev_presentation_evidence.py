#!/usr/bin/env python3
"""Render sanitized Jev evaluation evidence for the study-group presentation."""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
from typing import Any


LABELS = ("CANCEL", "CONFIRM", "DOCK", "SPRAY", "UNDOCK", "UNKNOWN")
BACKENDS = ("local", "jev")
SOURCE_SCOPE = "n=60, corpus sintetico pareado, uma rodada remota"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Gera evidencia de apresentacao a partir das metricas Jev.")
    parser.add_argument("--metrics", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def load_metrics(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != "1.0" or not isinstance(payload.get("backends"), dict):
        raise ValueError("unsupported Jev metrics schema")
    if set(payload["backends"]) != set(BACKENDS):
        raise ValueError("metrics must contain local and jev backends")
    for backend in BACKENDS:
        validate_backend(backend, payload["backends"][backend])
    if payload["backends"]["local"]["examples"] != payload["backends"]["jev"]["examples"]:
        raise ValueError("backend example counts must match")
    return payload


def validate_backend(name: str, value: Any) -> None:
    if not isinstance(value, dict) or not isinstance(value.get("examples"), int) or value["examples"] <= 0:
        raise ValueError(f"{name}: invalid example count")
    matrix = value.get("confusion_matrix")
    if not isinstance(matrix, dict) or set(matrix) != set(LABELS):
        raise ValueError(f"{name}: invalid confusion matrix rows")
    if any(not isinstance(row, dict) or set(row) != set(LABELS) for row in matrix.values()):
        raise ValueError(f"{name}: invalid confusion matrix columns")
    calibration = value.get("calibration")
    bins = calibration.get("reliability_bins") if isinstance(calibration, dict) else None
    if not isinstance(bins, list) or len(bins) != 10:
        raise ValueError(f"{name}: invalid reliability bins")
    if any(not isinstance(bin_, dict) or not isinstance(bin_.get("examples"), int) for bin_ in bins):
        raise ValueError(f"{name}: invalid reliability bin")


def build_evidence(metrics: dict[str, Any], source_sha256: str) -> dict[str, Any]:
    backends = {}
    for backend in BACKENDS:
        values = metrics["backends"][backend]
        backends[backend] = {
            "examples": values["examples"],
            "correct": values["correct"],
            "accuracy": values["accuracy"],
            "macro_f1": values["macro_f1"],
            "unsafe_accepts": values["unsafe_accepts"],
            "failure_rate": values["failure_rate"],
            "failures": values["failures"],
            "probability_coverage": values["probability_coverage"],
            "calibration": {
                "brier_multiclass": values["calibration"]["brier_multiclass"],
                "top_label_ece": values["calibration"]["top_label_ece"],
                "occupied_bins": [
                    bin_ for bin_ in values["calibration"]["reliability_bins"]
                    if bin_["examples"] > 0
                ],
            },
            "latency_ms": values["latency_ms"],
            "cost_usd": values["cost_usd"],
            "models": values["models"],
            "confusion_matrix": values["confusion_matrix"],
        }
    return {
        "schema_version": "1.0",
        "source_metrics_sha256": source_sha256,
        "scope": SOURCE_SCOPE,
        "limitation": "Descritivo: nao prova calibracao generalizavel, seguranca de campo ou prontidao operacional.",
        "backends": backends,
    }


def render_markdown(evidence: dict[str, Any]) -> str:
    local = evidence["backends"]["local"]
    jev = evidence["backends"]["jev"]
    lines = [
        "# Evidencia Jev - Avaliacao Final de Recuperacao",
        "",
        f"Escopo: {evidence['scope']}.",
        "",
        "## Comparacao medida",
        "",
        "| Medida | Local | Jev remoto |",
        "| --- | ---: | ---: |",
        f"| Casos | {local['examples']} | {jev['examples']} |",
        f"| Acertos | {local['correct']} | {jev['correct']} |",
        f"| Accuracy | {format_number(local['accuracy'])} | {format_number(jev['accuracy'])} |",
        f"| Macro-F1 | {format_number(local['macro_f1'])} | {format_number(jev['macro_f1'])} |",
        f"| Aceitacoes inseguras | {len(local['unsafe_accepts'])} | {len(jev['unsafe_accepts'])} |",
        f"| Brier multiclasses | {format_number(local['calibration']['brier_multiclass'])} | {format_number(jev['calibration']['brier_multiclass'])} |",
        f"| Top-label ECE | {format_number(local['calibration']['top_label_ece'])} | {format_number(jev['calibration']['top_label_ece'])} |",
        f"| Coverage de probabilidades | {format_number(local['probability_coverage'])} | {format_number(jev['probability_coverage'])} |",
        f"| Falhas remotas | {len(local['failures'])} | {len(jev['failures'])} |",
        f"| Latencia p50 | {format_ms(local['latency_ms']['p50'])} | {format_ms(jev['latency_ms']['p50'])} |",
        f"| Latencia p95 | {format_ms(local['latency_ms']['p95'])} | {format_ms(jev['latency_ms']['p95'])} |",
        f"| Custo | {format_usd(local['cost_usd']['total'])} | {format_usd(jev['cost_usd']['total'])} |",
        f"| Modelo | - | {', '.join(jev['models']) or '-'} |",
        "",
        "## Matriz de confusao",
        "",
        "Linhas sao rotulos ouro; colunas sao predicoes operacionais.",
        "",
        "### Local",
        "",
        *matrix_markdown(local["confusion_matrix"]),
        "",
        "### Jev remoto",
        "",
        *matrix_markdown(jev["confusion_matrix"]),
        "",
        "## Aceitacoes inseguras medidas",
        "",
        *unsafe_markdown("Local", local["unsafe_accepts"]),
        *unsafe_markdown("Jev remoto", jev["unsafe_accepts"]),
        "",
        "## Reliability diagram",
        "",
        "O SVG pareado mostra somente bins ocupados. Cada ponto informa `n`; a diagonal representa calibracao ideal.",
        "",
        "- [jev-final-recovery-reliability.svg](jev-final-recovery-reliability.svg)",
        "",
        "## Limites de interpretacao",
        "",
        f"{evidence['limitation']} A amostra tem 60 falas sinteticas, uma unica rodada e nao possui intervalo de confianca ou replicacao.",
        "Latencia e custo sao medidos no harness deste host; nao representam Android, audio, rede de campo ou controle do robo.",
        "O aceite Jev `CANCEL -> CONFIRM` impede qualquer alegacao de seguranca operacional. A decisao de adocao pertence a JEV-43.",
        "",
        f"Proveniencia: SHA-256 das metricas de entrada `{evidence['source_metrics_sha256']}`.",
        "",
    ]
    return "\n".join(lines)


def matrix_markdown(matrix: dict[str, dict[str, int]]) -> list[str]:
    lines = ["| Ouro \\ Predicao | " + " | ".join(LABELS) + " |", "| --- |" + " ---: |" * len(LABELS)]
    lines.extend("| " + label + " | " + " | ".join(str(matrix[label][predicted]) for predicted in LABELS) + " |" for label in LABELS)
    return lines


def unsafe_markdown(name: str, values: list[dict[str, Any]]) -> list[str]:
    if not values:
        return [f"- {name}: nenhum aceite inseguro."]
    cases = "`, `".join(
        f"{value['id']} {value['gold_label']} -> {value['predicted_label']} ({format_number(value['confidence'])})"
        for value in values
    )
    return [
        f"- {name}: `{cases}`."
    ]


def render_svg(evidence: dict[str, Any]) -> str:
    width, height = 1000, 560
    panel_width, panel_height, top, left = 400, 320, 150, 78
    panels = (("local", "Local", "#0f766e", left), ("jev", "Jev remoto", "#b45309", 530))
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        '<title id="title">Reliability diagram Local e Jev</title>',
        '<desc id="desc">Confianca media do top-label no eixo horizontal e accuracy observada no eixo vertical. Cada ponto e um bin ocupado.</desc>',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<text x="50" y="36" font-family="sans-serif" font-size="22" font-weight="700" fill="#1f2937">Reliability diagram: Local e Jev remoto</text>',
        f'<text x="50" y="62" font-family="sans-serif" font-size="14" fill="#374151">{html.escape(SOURCE_SCOPE)}. Descritivo; nao prova calibracao generalizavel.</text>',
    ]
    for key, title, color, x0 in panels:
        elements.extend(panel_svg(evidence["backends"][key]["calibration"]["occupied_bins"], title, color, x0, top, panel_width, panel_height))
    elements.extend([
        '<text x="50" y="520" font-family="sans-serif" font-size="13" fill="#374151">Eixo x: confianca media do top-label. Eixo y: accuracy observada. Diagonal: calibracao ideal.</text>',
        '<text x="50" y="542" font-family="sans-serif" font-size="13" fill="#991b1b">Leitura obrigatoria: ha um aceite inseguro Jev CANCEL -> CONFIRM; nao usar este grafico como prova de seguranca.</text>',
        '</svg>',
    ])
    return "\n".join(elements) + "\n"


def panel_svg(bins: list[dict[str, Any]], title: str, color: str, x0: int, y0: int, width: int, height: int) -> list[str]:
    bottom = y0 + height
    elements = [
        f'<text x="{x0}" y="118" font-family="sans-serif" font-size="18" font-weight="700" fill="#1f2937">{title}</text>',
        f'<rect x="{x0}" y="{y0}" width="{width}" height="{height}" fill="#ffffff" stroke="#4b5563"/>',
        f'<line x1="{x0}" y1="{bottom}" x2="{x0 + width}" y2="{y0}" stroke="#6b7280" stroke-dasharray="6 5"/>',
    ]
    for tick in (0.0, 0.5, 1.0):
        x = x0 + tick * width
        y = bottom - tick * height
        elements.extend([
            f'<line x1="{x}" y1="{bottom}" x2="{x}" y2="{bottom + 5}" stroke="#4b5563"/>',
            f'<text x="{x}" y="{bottom + 23}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">{tick:.1f}</text>',
            f'<line x1="{x0 - 5}" y1="{y}" x2="{x0}" y2="{y}" stroke="#4b5563"/>',
            f'<text x="{x0 - 10}" y="{y + 4}" text-anchor="end" font-family="sans-serif" font-size="12" fill="#1f2937">{tick:.1f}</text>',
        ])
    for index, bin_ in enumerate(bins):
        confidence = float(bin_["confidence"])
        accuracy = float(bin_["accuracy"])
        x = x0 + confidence * width
        y = bottom - accuracy * height
        radius = 8 + min(10, int(bin_["examples"]) // 2)
        label_y = y - radius - (8 if index % 2 == 0 else 20)
        elements.extend([
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius}" fill="{color}" fill-opacity="0.82" stroke="#1f2937" stroke-width="1.2"/>',
            f'<text x="{x:.2f}" y="{label_y:.2f}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#1f2937">n={bin_["examples"]}</text>',
        ])
    elements.extend([
        f'<text x="{x0 + width / 2}" y="{bottom + 56}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#1f2937">Confianca media</text>',
        f'<text x="{x0 - 56}" y="{y0 + height / 2}" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#1f2937" transform="rotate(-90 {x0 - 56} {y0 + height / 2})">Accuracy observada</text>',
    ])
    return elements


def format_number(value: float | None) -> str:
    return "-" if value is None else f"{value:.4f}".replace(".", ",")


def format_ms(value: float | None) -> str:
    return "-" if value is None else f"{value:.3f} ms".replace(".", ",")


def format_usd(value: float | None) -> str:
    return "-" if value is None else f"US${value:.9f}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_artifacts(metrics_path: Path, output_dir: Path) -> dict[str, Path]:
    evidence = build_evidence(load_metrics(metrics_path), sha256(metrics_path))
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": output_dir / "jev-final-recovery-presentation.json",
        "markdown": output_dir / "jev-final-recovery-presentation.md",
        "svg": output_dir / "jev-final-recovery-reliability.svg",
    }
    paths["json"].write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    paths["markdown"].write_text(render_markdown(evidence), encoding="utf-8")
    paths["svg"].write_text(render_svg(evidence), encoding="utf-8")
    return paths


def main() -> None:
    args = parse_args()
    paths = write_artifacts(args.metrics, args.output_dir)
    print(f"wrote presentation evidence to {paths['markdown']}")


if __name__ == "__main__":
    main()
