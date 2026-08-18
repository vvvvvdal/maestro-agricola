from __future__ import annotations

import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 18765


@dataclass(frozen=True)
class Check:
    level: str
    name: str
    detail: str


def run(command: list[str], timeout: float = 8) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def command_check(name: str, command: list[str]) -> Check:
    if shutil.which(command[0]) is None:
        return Check("ERRO", name, f"comando `{command[0]}` não encontrado")
    try:
        result = run(command)
    except subprocess.TimeoutExpired:
        return Check("ERRO", name, "comando excedeu o tempo de diagnóstico")
    first_line = (result.stdout.strip().splitlines() or ["sem saída"])[0]
    if result.returncode:
        return Check("ERRO", name, first_line)
    return Check("OK", name, first_line)


def artifact_check() -> Check:
    expected = [
        ROOT / "compose.yaml",
        ROOT / "shared/ai/intent_model.json",
        ROOT / "contracts/command.schema.json",
        ROOT / "robot_ws/src/maestro_simulation/launch/demo.launch.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in expected if not path.is_file()]
    if missing:
        return Check("ERRO", "arquivos do MVP", "ausentes: " + ", ".join(missing))
    return Check("OK", "arquivos do MVP", "contrato, modelo e launch encontrados")


def docker_daemon_check() -> Check:
    if shutil.which("docker") is None:
        return Check("ERRO", "Docker daemon", "Docker não instalado")
    try:
        result = run(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=10)
    except subprocess.TimeoutExpired:
        return Check("ERRO", "Docker daemon", "não respondeu em 10 s")
    if result.returncode:
        detail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else "indisponível"
        return Check(
            "ERRO",
            "Docker daemon",
            detail + "; inicie o Docker e confirme que seu usuário tem permissão",
        )
    return Check("OK", "Docker daemon", f"servidor {result.stdout.strip()}")


def websocket_check() -> Check:
    try:
        connection = socket.create_connection((DEFAULT_HOST, DEFAULT_PORT), timeout=0.8)
    except (ConnectionRefusedError, TimeoutError, OSError):
        return Check(
            "INFO",
            "bridge WebSocket",
            f"ainda não iniciado em ws://{DEFAULT_HOST}:{DEFAULT_PORT}; `make demo` irá iniciá-lo",
        )
    connection.close()

    try:
        from websockets.sync.client import connect

        with connect(
            f"ws://{DEFAULT_HOST}:{DEFAULT_PORT}",
            open_timeout=2,
            close_timeout=1,
            proxy=None,
        ):
            pass
    except Exception as error:  # diagnostic must report third-party protocol details
        return Check(
            "ERRO",
            "bridge WebSocket",
            f"porta {DEFAULT_PORT} ocupada, mas não responde como Maestro WebSocket: {error}",
        )
    return Check("OK", "bridge WebSocket", f"respondendo em ws://{DEFAULT_HOST}:{DEFAULT_PORT}")


def main() -> None:
    python_ok = sys.version_info >= (3, 10)
    checks = [
        Check(
            "OK" if python_ok else "ERRO",
            "Python",
            f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        ),
        command_check("Docker CLI", ["docker", "--version"]),
        command_check("Docker Compose", ["docker", "compose", "version"]),
        artifact_check(),
        docker_daemon_check(),
        websocket_check(),
    ]

    width = max(len(check.name) for check in checks)
    print("Diagnóstico do Maestro Agrícola")
    for check in checks:
        print(f"[{check.level:4}] {check.name:<{width}} - {check.detail}")

    errors = [check for check in checks if check.level == "ERRO"]
    if errors:
        print("\nCorrija os itens [ERRO] antes de executar `make demo`.")
        raise SystemExit(1)
    print("\nAmbiente pronto. Execute `make demo`.")


if __name__ == "__main__":
    main()
