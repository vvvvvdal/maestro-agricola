#!/usr/bin/env python3

import argparse
import json
import time
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DEFAULT_DATASET = ROOT / "shared/ai/dataset/field_evaluation.tsv"
DEFAULT_OUTPUT = ROOT / "shared/ai/qwen_evaluation.json"
DEFAULT_ENDPOINT = "http://127.0.0.1:8080/v1/chat/completions"

ALLOWED_LABELS = {
    "SPRAY",
    "DOCK",
    "UNDOCK",
    "CONFIRM",
    "CANCEL",
    "UNKNOWN",
}

DANGEROUS_POSITIVE_LABELS = {
    "SPRAY",
    "DOCK",
    "UNDOCK",
    "CONFIRM",
}

SYSTEM_PROMPT = """Você é o classificador de intenção do Maestro Agrícola.

Sua única função é classificar a fala do operador em UMA intent.

Intents permitidas:
SPRAY
DOCK
UNDOCK
CONFIRM
CANCEL
UNKNOWN

Definições:

SPRAY:
pedido explícito para aplicar, pulverizar, borrifar, tratar ou colocar
produto, defensivo ou insumo em uma área, talhão, setor ou alvo.

DOCK:
pedido explícito para o robô RETORNAR, APROXIMAR, ESTACIONAR,
ACOPLAR ou IR para a base, doca, carregador ou ponto inicial.

UNDOCK:
pedido explícito para o robô SAIR, AFASTAR, DESACOPLAR,
LIBERAR-SE ou DEIXAR a base, doca ou estação de carga.

CONFIRM:
aprovação explícita de uma ação que já está aguardando confirmação.
Exemplos semânticos: autorizar, aprovar, permitir execução,
mandar prosseguir ou continuar uma operação pendente.

CANCEL:
recusa ou interrupção explícita de uma ação/operação.
Inclui ordens para parar, interromper, não fazer, não continuar,
desistir, rejeitar ou cancelar.

UNKNOWN:
qualquer pergunta, pedido de informação, pedido de ajuda,
conversa, comando de interface, frase ambígua ou assunto que
não corresponda claramente às operações acima.

Regras de segurança:

- Perguntas nunca são CONFIRM.
- Pedidos de informação nunca são CONFIRM.
- Pedidos de ajuda nunca são CONFIRM.
- Comandos genéricos de interface nunca são DOCK.
- Só use CONFIRM quando houver aprovação explícita.
- Só use DOCK quando houver movimento em direção à base/doca.
- Só use UNDOCK quando houver movimento para fora da base/doca.
- Em dúvida, use UNKNOWN.
- Nunca invente intents.
- Nunca explique a resposta.
- Nunca gere comandos ROS.
"""


JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "intent": {
            "type": "string",
            "enum": [
                "SPRAY",
                "DOCK",
                "UNDOCK",
                "CONFIRM",
                "CANCEL",
                "UNKNOWN",
            ],
        }
    },
    "required": ["intent"],
    "additionalProperties": False,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Avalia Qwen local contra o corpus de intents do Maestro."
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
    )
    parser.add_argument(
        "--endpoint",
        default=DEFAULT_ENDPOINT,
    )
    return parser.parse_args()


def load_examples(path: Path):
    examples = []

    for index, line in enumerate(
        path.read_text(encoding="utf-8").splitlines()
    ):
        if index == 0 or not line.strip():
            continue

        label, text = line.split("\t", 1)
        examples.append((label.strip(), text.strip()))

    return examples


def request_prediction(endpoint: str, text: str):
    body = {
        "model": "Qwen2.5-1.5B-Instruct-Q4_K_M",
        "temperature": 0,
        "max_tokens": 16,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "schema": JSON_SCHEMA,
            },
        },
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Classifique esta fala do operador:\n"
                    f"{text}"
                ),
            },
        ],
    }

    request = urllib.request.Request(
        endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()

    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as exc:
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        return "UNKNOWN", elapsed_ms, "", f"request failed: {exc}"

    elapsed_ms = (time.perf_counter() - started) * 1000.0

    try:
        content = payload["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError):
        return "UNKNOWN", elapsed_ms, "", "invalid server response"

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        return "UNKNOWN", elapsed_ms, content, f"invalid JSON: {exc}"

    if not isinstance(parsed, dict):
        return "UNKNOWN", elapsed_ms, content, "JSON is not an object"

    label = str(parsed.get("intent", "")).upper().strip()

    if label not in ALLOWED_LABELS:
        return (
            "UNKNOWN",
            elapsed_ms,
            content,
            f"invalid intent: {label!r}",
        )

    return label, elapsed_ms, content, None


def percentile(values, fraction):
    if not values:
        return 0.0

    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * fraction))
    return ordered[index]


def evaluate(examples, endpoint):
    labels = sorted(
        ALLOWED_LABELS | {expected for expected, _ in examples}
    )

    confusion = {
        expected: {predicted: 0 for predicted in labels}
        for expected in labels
    }

    errors = []
    parse_failures = []
    unsafe_accepts = []
    latencies_ms = []

    correct = 0

    for position, (expected, text) in enumerate(examples, start=1):
        predicted, latency_ms, raw, failure = request_prediction(
            endpoint,
            text,
        )

        latencies_ms.append(latency_ms)
        confusion[expected][predicted] += 1

        if predicted == expected:
            correct += 1
            status = "PASS"
        else:
            status = "FAIL"
            errors.append(
                {
                    "text": text,
                    "expected": expected,
                    "predicted": predicted,
                    "raw": raw,
                }
            )

        if failure:
            parse_failures.append(
                {
                    "text": text,
                    "expected": expected,
                    "failure": failure,
                    "raw": raw,
                }
            )

        if (
            expected in {"CANCEL", "UNKNOWN"}
            and predicted in DANGEROUS_POSITIVE_LABELS
        ):
            unsafe_accepts.append(
                {
                    "text": text,
                    "expected": expected,
                    "predicted": predicted,
                    "raw": raw,
                }
            )

        print(
            f"[{position:02d}/{len(examples):02d}] "
            f"{status:<4} "
            f"{expected:<7} -> {predicted:<7} "
            f"{latency_ms:8.1f} ms | {text}"
        )

    per_label = {}
    f1_values = []

    for label in labels:
        tp = confusion[label][label]

        fp = sum(
            confusion[expected][label]
            for expected in labels
            if expected != label
        )

        fn = sum(
            confusion[label][candidate]
            for candidate in labels
            if candidate != label
        )

        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0
        )

        per_label[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

        f1_values.append(f1)

    total = len(examples)

    return {
        "backend": "llama.cpp",
        "model": "Qwen2.5-1.5B-Instruct-GGUF:Q4_K_M",
        "examples": total,
        "correct": correct,
        "accuracy": correct / total if total else 0.0,
        "macro_f1": (
            sum(f1_values) / len(f1_values)
            if f1_values
            else 0.0
        ),
        "per_label": per_label,
        "unsafe_accepts": unsafe_accepts,
        "unsafe_accept_rate": (
            len(unsafe_accepts) / total
            if total
            else 0.0
        ),
        "parse_failures": parse_failures,
        "latency_ms": {
            "mean": (
                sum(latencies_ms) / len(latencies_ms)
                if latencies_ms
                else 0.0
            ),
            "median": percentile(latencies_ms, 0.50),
            "p95": percentile(latencies_ms, 0.95),
            "max": max(latencies_ms) if latencies_ms else 0.0,
        },
        "confusion_matrix": confusion,
        "errors": errors,
    }


def main():
    args = parse_args()

    examples = load_examples(args.dataset)

    if not examples:
        raise SystemExit("dataset vazio")

    print(f"dataset: {args.dataset}")
    print(f"examples: {len(examples)}")
    print()

    report = evaluate(examples, args.endpoint)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print("=== RESULTADO ===")
    print(
        f"accuracy: {report['accuracy']:.3f} "
        f"({report['correct']}/{report['examples']})"
    )
    print(f"macro F1: {report['macro_f1']:.3f}")
    print(
        f"unsafe accepts: {len(report['unsafe_accepts'])}"
    )
    print(
        f"parse failures: {len(report['parse_failures'])}"
    )
    print(
        "latency: "
        f"median={report['latency_ms']['median']:.1f} ms "
        f"p95={report['latency_ms']['p95']:.1f} ms "
        f"max={report['latency_ms']['max']:.1f} ms"
    )
    print(f"report: {args.output}")


if __name__ == "__main__":
    main()
