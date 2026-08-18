#!/usr/bin/env python3
"""Checks the local toolchain before attempting the iOS mock build."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys


REQUIRED_XCODE = (26, 4)
REQUIRED_SWIFT = (6, 3)
REQUIRED_XCODEGEN = (2, 44, 1)


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def parse_version(output: str, pattern: str) -> tuple[int, ...] | None:
    match = re.search(pattern, output, flags=re.IGNORECASE)
    if not match:
        return None
    return tuple(int(part) for part in match.group(1).split("."))


def version_at_least(actual: tuple[int, ...] | None, required: tuple[int, ...]) -> bool:
    if actual is None:
        return False
    size = max(len(actual), len(required))
    return actual + (0,) * (size - len(actual)) >= required + (0,) * (size - len(required))


def version_text(value: tuple[int, ...] | None) -> str:
    return ".".join(map(str, value)) if value else "desconhecida"


def command_output(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def tool_check(
    name: str,
    executable: str,
    arguments: list[str],
    pattern: str,
    required: tuple[int, ...],
) -> Check:
    path = shutil.which(executable)
    if not path:
        return Check(name, False, f"{executable} não encontrado")
    result = command_output([path, *arguments])
    output = "\n".join((result.stdout, result.stderr))
    version = parse_version(output, pattern)
    return Check(
        name,
        result.returncode == 0 and version_at_least(version, required),
        f"{path} (versão {version_text(version)}; mínimo {version_text(required)})",
    )


def project_checks(project_dir: Path) -> list[Check]:
    project_yml = project_dir / "project.yml"
    info_plist = project_dir / "MaestroAgricola" / "Info.plist"
    model = project_dir.parents[1] / "shared" / "ai" / "intent_model.json"
    checks = [
        Check("project.yml", project_yml.is_file(), str(project_yml)),
        Check("Info.plist", info_plist.is_file(), str(info_plist)),
        Check("Modelo local", model.is_file(), str(model)),
    ]
    if project_yml.is_file():
        content = project_yml.read_text(encoding="utf-8")
        reference = "../../shared/ai/intent_model.json"
        checks.append(Check("Modelo no projeto", reference in content, reference))
    return checks


def collect_checks(project_dir: Path) -> list[Check]:
    checks = [
        Check("Host macOS", platform.system() == "Darwin", platform.platform()),
        tool_check("Xcode", "xcodebuild", ["-version"], r"Xcode\s+(\d+(?:\.\d+)+)", REQUIRED_XCODE),
        tool_check("Swift", "swift", ["--version"], r"Swift\s+(?:version\s+)?(\d+(?:\.\d+)+)", REQUIRED_SWIFT),
        tool_check("XcodeGen", "xcodegen", ["--version"], r"(?:Version:\s*)?(\d+(?:\.\d+)+)", REQUIRED_XCODEGEN),
    ]
    return checks + project_checks(project_dir)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Diretório mobile/ios",
    )
    args = parser.parse_args()

    checks = collect_checks(args.project_dir.resolve())
    print("Preflight iOS mock")
    for check in checks:
        marker = "OK" if check.ok else "ERRO"
        print(f"[{marker:4}] {check.name:20} - {check.detail}")

    if any(not check.ok for check in checks):
        print("\nCorrija os itens [ERRO] no Mac antes do build. Nenhum build iOS foi declarado como aprovado.")
        return 1

    print("\nToolchain pronta. Próximos comandos:")
    print("  cd mobile/ios")
    print("  xcodegen generate")
    print("  xcodebuild test -project MaestroAgricola.xcodeproj -scheme MaestroAgricola \\")
    print("    -destination 'platform=iOS Simulator,name=iPhone 13'")
    print("Depois, abra o projeto e execute no iPhone físico para validar voz, TTS e assinatura.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
