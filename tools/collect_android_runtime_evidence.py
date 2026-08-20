#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APK = ROOT / "mobile" / "android" / "app" / "build" / "outputs" / "apk" / "mock" / "debug" / "app-mock-debug.apk"
DEFAULT_MODEL = ROOT / "shared" / "ai" / "intent_model.json"
DEFAULT_PACKAGE = "br.org.agroturtles.maestro.mock"
PACKAGE_PATTERN = re.compile(r"^[A-Za-z0-9_.]+$")
PHASE_PATTERN = re.compile(r"^[a-z0-9_-]+$")
MEDIA_SUFFIXES = {
    ".aac", ".flac", ".heic", ".jpeg", ".jpg", ".m4a", ".mp3", ".mp4",
    ".ogg", ".pcm", ".png", ".wav", ".webm", ".webp",
}
SUSPICIOUS_NAME_TOKENS = {
    "audio", "capture", "frame", "image", "photo", "recording", "transcript", "voice",
}
THERMAL_STATUS_NAMES = {
    0: "NONE",
    1: "LIGHT",
    2: "MODERATE",
    3: "SEVERE",
    4: "CRITICAL",
    5: "EMERGENCY",
    6: "SHUTDOWN",
}


class CollectionError(RuntimeError):
    pass


Query = Callable[[list[str]], str]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_adb_devices(output: str) -> dict[str, str]:
    devices: dict[str, str] = {}
    for raw_line in output.splitlines()[1:]:
        fields = raw_line.strip().split()
        if len(fields) >= 2:
            devices[fields[0]] = fields[1]
    return devices


def parse_key_values(output: str) -> dict[str, int]:
    values: dict[str, int] = {}
    for raw_line in output.splitlines():
        match = re.match(r"\s*([A-Za-z][A-Za-z ]+):\s*(-?\d+)\s*$", raw_line)
        if match:
            values[match.group(1).strip().lower().replace(" ", "_")] = int(match.group(2))
    return values


def parse_package_info(output: str) -> dict[str, Any]:
    if "Unable to find package" in output:
        raise CollectionError("pacote Android não encontrado")
    version_name = re.search(r"\bversionName=([^\s]+)", output)
    version_code = re.search(r"\bversionCode=(\d+)", output)
    return {
        "version_name": version_name.group(1) if version_name else None,
        "version_code": int(version_code.group(1)) if version_code else None,
    }


def parse_thermal_status(output: str) -> dict[str, Any] | None:
    match = re.search(r"Thermal Status:\s*(\d+)", output, re.IGNORECASE)
    if not match:
        return None
    value = int(match.group(1))
    return {"code": value, "name": THERMAL_STATUS_NAMES.get(value, "UNKNOWN")}


def parse_total_pss_kb(output: str) -> int | None:
    match = re.search(r"TOTAL PSS:\s*([\d,]+)", output)
    if not match:
        match = re.search(r"^\s*TOTAL\s+([\d,]+)\b", output, re.MULTILINE)
    return int(match.group(1).replace(",", "")) if match else None


def parse_file_paths(output: str) -> list[str]:
    paths: list[str] = []
    for raw_line in output.splitlines():
        path = raw_line.strip()
        if not path or "Permission denied" in path or path.startswith("find:"):
            continue
        paths.append(path[:500])
    return sorted(set(paths))


def suspicious_paths(paths: list[str]) -> list[str]:
    flagged: list[str] = []
    for path in paths:
        lowered = path.lower()
        suffix = Path(lowered).suffix
        tokens = set(re.findall(r"[a-z]+", Path(lowered).name))
        if suffix in MEDIA_SUFFIXES or tokens.intersection(SUSPICIOUS_NAME_TOKENS):
            flagged.append(path)
    return flagged[:50]


def optional_query(query: Query, args: list[str]) -> tuple[bool, str]:
    try:
        return True, query(args)
    except CollectionError:
        return False, ""


def build_runtime_evidence(
    query: Query,
    package: str,
    phase: str,
    apk_path: Path,
    model_path: Path,
    recorded_at: str | None = None,
) -> dict[str, Any]:
    if not PACKAGE_PATTERN.fullmatch(package):
        raise ValueError("package Android inválido")
    if not PHASE_PATTERN.fullmatch(phase):
        raise ValueError("phase deve conter apenas letras minúsculas, números, hífen ou sublinhado")
    if not apk_path.is_file():
        raise CollectionError(f"APK não encontrado: {apk_path}")
    if not model_path.is_file():
        raise CollectionError(f"modelo não encontrado: {model_path}")
    if query(["get-state"]).strip() != "device":
        raise CollectionError("dispositivo adb não está pronto")

    properties = {
        "manufacturer": query(["shell", "getprop", "ro.product.manufacturer"]).strip(),
        "model": query(["shell", "getprop", "ro.product.model"]).strip(),
        "android_release": query(["shell", "getprop", "ro.build.version.release"]).strip(),
        "android_api": int(query(["shell", "getprop", "ro.build.version.sdk"]).strip()),
        "abis": [value for value in query(["shell", "getprop", "ro.product.cpu.abilist"]).strip().split(",") if value],
    }
    package_info = parse_package_info(query(["shell", "dumpsys", "package", package]))

    battery_values = parse_key_values(query(["shell", "dumpsys", "battery"]))
    battery = {
        "level_percent": battery_values.get("level"),
        "temperature_c": (
            battery_values["temperature"] / 10.0 if "temperature" in battery_values else None
        ),
        "voltage_mv": battery_values.get("voltage"),
        "status_code": battery_values.get("status"),
        "plugged_code": battery_values.get("plugged"),
    }

    thermal_available, thermal_output = optional_query(query, ["shell", "dumpsys", "thermalservice"])
    memory_available, memory_output = optional_query(query, ["shell", "dumpsys", "meminfo", package])
    internal_available, internal_output = optional_query(
        query, ["shell", "run-as", package, "find", ".", "-type", "f"]
    )
    external_available, external_output = optional_query(
        query, ["shell", "find", f"/sdcard/Android/data/{package}", "-type", "f"]
    )

    internal_paths = parse_file_paths(internal_output) if internal_available else []
    external_paths = parse_file_paths(external_output) if external_available else []
    internal_suspicious = suspicious_paths(internal_paths)
    external_suspicious = suspicious_paths(external_paths)
    suspicious_count = len(internal_suspicious) + len(external_suspicious)
    scans_complete = internal_available and external_available
    collection_status = (
        "REVIEW_REQUIRED" if suspicious_count else ("COMPLETE" if scans_complete else "PARTIAL")
    )

    return {
        "schema_version": "1.0",
        "recorded_at": recorded_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "phase": phase,
        "collection_status": collection_status,
        "scope": "Metadados técnicos Android sem mídia, logcat ou conteúdo de arquivos",
        "package": package,
        "device": properties,
        "build": {
            **package_info,
            "apk_sha256": sha256_file(apk_path),
            "model_sha256": sha256_file(model_path),
        },
        "battery": battery,
        "thermal": {
            "scan_available": thermal_available,
            "status": parse_thermal_status(thermal_output) if thermal_available else None,
        },
        "memory": {
            "scan_available": memory_available,
            "total_pss_kb": parse_total_pss_kb(memory_output) if memory_available else None,
        },
        "storage_audit": {
            "internal": {
                "scan_available": internal_available,
                "file_count": len(internal_paths),
                "suspicious_file_count": len(internal_suspicious),
                "suspicious_paths": internal_suspicious,
            },
            "external": {
                "scan_available": external_available,
                "file_count": len(external_paths),
                "suspicious_file_count": len(external_suspicious),
                "suspicious_paths": external_suspicious,
            },
            "limitation": "Caminhos e contagens não comprovam o conteúdo de bancos, preferências ou caches do sistema",
        },
        "privacy": {
            "captures_logcat": False,
            "reads_file_contents": False,
            "captures_audio": False,
            "captures_images": False,
            "captures_transcripts": False,
            "stores_device_serial": False,
        },
    }


def resolve_adb() -> Path:
    executable = shutil.which("adb")
    if executable:
        return Path(executable)
    local_properties = ROOT / "mobile" / "android" / "local.properties"
    if local_properties.is_file():
        for raw_line in local_properties.read_text(encoding="utf-8").splitlines():
            if raw_line.strip().startswith("sdk.dir="):
                sdk = raw_line.split("=", 1)[1].replace("\\:", ":").replace("\\\\", "\\")
                candidate = Path(sdk).expanduser() / "platform-tools" / "adb"
                if candidate.is_file():
                    return candidate
    raise CollectionError("adb não encontrado")


def command_output(command: list[str], timeout: int = 15) -> str:
    result = subprocess.run(command, capture_output=True, text=True, check=False, timeout=timeout)
    if result.returncode != 0:
        raise CollectionError(f"comando técnico falhou com código {result.returncode}: {command[-3:]}")
    return result.stdout


def select_device(adb: Path, requested_serial: str | None) -> str:
    devices = parse_adb_devices(command_output([str(adb), "devices"]))
    if requested_serial:
        if devices.get(requested_serial) != "device":
            raise CollectionError("serial solicitado não está autorizado no adb")
        return requested_serial
    ready = [serial for serial, state in devices.items() if state == "device"]
    if len(ready) != 1:
        raise CollectionError("conecte exatamente um aparelho ou informe --serial")
    return ready[0]


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta metadados Android para QA-03/QA-04 sem mídia bruta")
    parser.add_argument("--phase", required=True, help="Identificador da coleta, por exemplo before ou after")
    parser.add_argument("--output", type=Path, help="JSON de saída; sem esta opção, imprime no terminal")
    parser.add_argument("--serial", help="Serial adb; não é gravado na evidência")
    parser.add_argument("--package", default=DEFAULT_PACKAGE)
    parser.add_argument("--apk", type=Path, default=DEFAULT_APK)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()

    try:
        adb = resolve_adb()
        serial = select_device(adb, args.serial)

        def query(command: list[str]) -> str:
            return command_output([str(adb), "-s", serial, *command])

        evidence = build_runtime_evidence(
            query,
            args.package,
            args.phase,
            args.apk.resolve(),
            args.model.resolve(),
        )
    except (CollectionError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print(f"Coleta Android não concluída: {error}", file=sys.stderr)
        return 1

    payload = json.dumps(evidence, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"Evidência Android salva em {output} ({evidence['collection_status']})")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
