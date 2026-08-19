#!/usr/bin/env python3
"""Checks the local toolchain before attempting the Android mock build."""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
import re
import shutil
import subprocess
import sys


REQUIRED_JAVA = 17
MAXIMUM_JAVA = 24
REQUIRED_PLATFORM = 36


@dataclass(frozen=True)
class Check:
    name: str
    ok: bool
    detail: str


def parse_java_major(output: str) -> int | None:
    match = re.search(r'version\s+"(?P<version>\d+)(?:\.(\d+))?', output)
    if not match:
        return None
    major = int(match.group("version"))
    if major == 1:
        legacy = re.search(r'version\s+"1\.(\d+)', output)
        return int(legacy.group(1)) if legacy else None
    return major


def is_supported_java_major(major: int | None) -> bool:
    return major is not None and REQUIRED_JAVA <= major <= MAXIMUM_JAVA


def read_sdk_dir(local_properties: Path) -> Path | None:
    if not local_properties.is_file():
        return None
    for raw_line in local_properties.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("sdk.dir="):
            value = line.removeprefix("sdk.dir=").replace("\\:", ":").replace("\\\\", "\\")
            return Path(value).expanduser()
    return None


def parse_adb_devices(output: str) -> dict[str, str]:
    devices: dict[str, str] = {}
    for raw_line in output.splitlines()[1:]:
        fields = raw_line.strip().split()
        if len(fields) >= 2:
            devices[fields[0]] = fields[1]
    return devices


def command_output(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=False)


def resolve_java(explicit_java_home: Path | None = None) -> Path | None:
    java_home = str(explicit_java_home) if explicit_java_home else os.environ.get("JAVA_HOME")
    if java_home:
        candidate = Path(java_home) / "bin" / "java"
        if candidate.is_file():
            return candidate
    executable = shutil.which("java")
    return Path(executable) if executable else None


def resolve_sdk(project_dir: Path, explicit_sdk_dir: Path | None = None) -> Path | None:
    if explicit_sdk_dir:
        return explicit_sdk_dir.expanduser()
    for variable in ("ANDROID_SDK_ROOT", "ANDROID_HOME"):
        value = os.environ.get(variable)
        if value:
            return Path(value).expanduser()
    return read_sdk_dir(project_dir / "local.properties")


def collect_checks(
    project_dir: Path,
    require_device: bool = False,
    java_home: Path | None = None,
    sdk_dir: Path | None = None,
) -> list[Check]:
    checks: list[Check] = []

    java = resolve_java(java_home)
    if java is None:
        checks.append(Check("JDK", False, "Java não encontrado; instale JDK 17 e configure JAVA_HOME"))
    else:
        result = command_output([str(java), "-version"])
        version_text = result.stderr or result.stdout
        major = parse_java_major(version_text)
        checks.append(Check(
            "JDK",
            result.returncode == 0
            and is_supported_java_major(major),
            f"{java} (versão {major or 'desconhecida'}; suportado {REQUIRED_JAVA}–{MAXIMUM_JAVA})",
        ))

    sdk = resolve_sdk(project_dir, sdk_dir)
    if sdk is None:
        checks.append(Check(
            "Android SDK",
            False,
            "SDK não encontrado; configure ANDROID_SDK_ROOT ou mobile/android/local.properties",
        ))
        adb = Path(shutil.which("adb")) if shutil.which("adb") else None
    else:
        checks.append(Check("Android SDK", sdk.is_dir(), str(sdk)))
        platform_jar = sdk / "platforms" / f"android-{REQUIRED_PLATFORM}" / "android.jar"
        checks.append(Check(f"Platform API {REQUIRED_PLATFORM}", platform_jar.is_file(), str(platform_jar)))
        sdk_adb = sdk / "platform-tools" / "adb"
        adb = sdk_adb if sdk_adb.is_file() else (Path(shutil.which("adb")) if shutil.which("adb") else None)

    gradlew = project_dir / "gradlew"
    wrapper_jar = project_dir / "gradle" / "wrapper" / "gradle-wrapper.jar"
    checks.append(Check("Gradle wrapper", gradlew.is_file() and wrapper_jar.is_file(), str(gradlew)))

    resources = project_dir / "app" / "src" / "main" / "res"
    icons = [resources / density / "ic_launcher.png" for density in (
        "mipmap-mdpi", "mipmap-hdpi", "mipmap-xhdpi", "mipmap-xxhdpi", "mipmap-xxxhdpi"
    )]
    fonts = [resources / "font" / filename for filename in (
        "league_spartan_regular.ttf", "league_spartan_medium.ttf",
        "league_spartan_semibold.ttf", "league_spartan_bold.ttf",
    )]
    checks.append(Check("Ícones da marca", all(path.is_file() for path in icons), str(icons[0].parent)))
    header_logo = resources / "drawable-nodpi" / "maestro_logo_horizontal.png"
    checks.append(Check("Lockup v2", header_logo.is_file(), str(header_logo)))
    checks.append(Check("League Spartan", all(path.is_file() for path in fonts), str(fonts[0].parent)))

    if require_device:
        if adb is None:
            checks.append(Check("Dispositivo Android", False, "adb não encontrado"))
        else:
            result = command_output([str(adb), "devices"])
            devices = parse_adb_devices(result.stdout)
            ready = [serial for serial, state in devices.items() if state == "device"]
            blocked = [f"{serial}:{state}" for serial, state in devices.items() if state != "device"]
            detail = f"prontos={ready or 'nenhum'}"
            if blocked:
                detail += f"; indisponíveis={blocked}"
            checks.append(Check("Dispositivo Android", result.returncode == 0 and bool(ready), detail))

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Diretório mobile/android",
    )
    parser.add_argument("--require-device", action="store_true", help="Exige ao menos um aparelho autorizado no adb")
    parser.add_argument("--java-home", type=Path, help="JDK desta execução, sem alterar JAVA_HOME")
    parser.add_argument("--sdk-dir", type=Path, help="Android SDK desta execução, sem criar local.properties")
    args = parser.parse_args()

    checks = collect_checks(
        args.project_dir.resolve(),
        args.require_device,
        args.java_home.expanduser().resolve() if args.java_home else None,
        args.sdk_dir.expanduser().resolve() if args.sdk_dir else None,
    )
    print("Preflight Android mock")
    for check in checks:
        marker = "OK" if check.ok else "ERRO"
        print(f"[{marker:4}] {check.name:22} - {check.detail}")

    if any(not check.ok for check in checks):
        print("\nCorrija os itens [ERRO] antes do build. Nenhum build foi declarado como aprovado.")
        return 1

    print("\nToolchain pronta. Próximos comandos:")
    print("  cd mobile/android")
    print("  ./gradlew testMockDebugUnitTest assembleMockDebug")
    if not args.require_device:
        print("  python3 tools/preflight.py --require-device  # antes de instalar no Android físico")
    return 0


if __name__ == "__main__":
    sys.exit(main())
