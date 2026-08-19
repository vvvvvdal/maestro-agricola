from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import os
import re
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SERVICE = os.environ.get("MAESTRO_SIMULATION_SERVICE", "simulation")


@dataclass(frozen=True)
class MissionLogStatus:
    undocked: bool
    completed_targets: tuple[str, ...]
    docked: bool
    failure: str | None = None


def run(command: list[str], timeout: float = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )


def compose(*args: str, timeout: float = 15) -> subprocess.CompletedProcess[str]:
    return run(["docker", "compose", *args], timeout=timeout)


def container_shell(script: str, timeout: float = 15) -> subprocess.CompletedProcess[str]:
    return compose(
        "exec", "-T", DEFAULT_SERVICE, "bash", "-lc", script, timeout=timeout
    )


def require_processes() -> None:
    result = container_shell(
        "pgrep -f '[i]gn gazebo' >/dev/null && "
        "pgrep -f '[b]ridge_node' >/dev/null",
    )
    if result.returncode:
        raise RuntimeError("Gazebo ou bridge não está ativo dentro do contêiner")


def recent_logs() -> str:
    result = compose("logs", "--since", "10m", DEFAULT_SERVICE, timeout=20)
    return result.stdout


def require_no_fatal_render_error() -> None:
    logs = recent_logs()
    fatal_markers = (
        "Unable to open display",
        "Server is already active for display",
        "[ign gazebo-1] Aborted",
        "[ERROR] [ign gazebo-1]: process has died",
    )
    found = [marker for marker in fatal_markers if marker in logs]
    if found:
        raise RuntimeError("falha fatal de renderização: " + ", ".join(found))


def wait_for_nav2(timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    command = (
        "source /opt/ros/humble/setup.bash && "
        "source /opt/maestro_ws/install/setup.bash && "
        "ros2 lifecycle get /turtlebot1/bt_navigator"
    )
    while time.monotonic() < deadline:
        require_processes()
        require_no_fatal_render_error()
        try:
            result = container_shell(command, timeout=10)
        except subprocess.TimeoutExpired:
            print("Consulta do Nav2 ocupada; tentando novamente...")
            time.sleep(3)
            continue
        if result.returncode == 0 and "active [3]" in result.stdout.lower():
            print("[OK] Nav2 ativo")
            return
        print("Aguardando Nav2 ficar ativo...")
        time.sleep(3)
    raise TimeoutError("Nav2 não ficou ativo dentro do tempo limite")


def wait_for_goal(timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        logs = recent_logs()
        if "Nav2 accepted command" in logs:
            print("[OK] Nav2 aceitou o comando")
            return
        require_processes()
        time.sleep(2)
    raise TimeoutError("o bridge não registrou aceite da meta pelo Nav2")


def evaluate_mission_logs(logs: str, expected_targets: list[str]) -> MissionLogStatus:
    undock_marker = "Undock completed: robot is clear of dock"
    undock_index = logs.rfind(undock_marker)
    if undock_index < 0:
        return MissionLogStatus(False, (), False)

    mission_logs = logs[undock_index:]
    fatal_markers = (
        "Mission lifecycle failed closed",
        "navigation timed out",
        "Nav2 rejected",
        "Nav2 ended with status=",
        "Nav2 result failed",
    )
    for marker in fatal_markers:
        if marker in mission_logs:
            return MissionLogStatus(True, (), False, marker)

    completed = []
    cursor = 0
    for target in expected_targets:
        pattern = re.compile(
            rf"Nav2 completed command [^\r\n]+ for target {re.escape(target)}"
        )
        match = pattern.search(mission_logs, cursor)
        if match is None:
            return MissionLogStatus(True, tuple(completed), False)
        completed.append(target)
        cursor = match.end()

    approach_index = mission_logs.find(
        "Nav2 completed return-to-dock approach", cursor
    )
    docked = (
        approach_index >= 0
        and mission_logs.find("Dock completed: robot is docked", approach_index) >= 0
    )
    return MissionLogStatus(True, tuple(completed), docked)


def wait_for_mission_cycle(expected_targets: list[str], timeout_seconds: float) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_progress = None
    while time.monotonic() < deadline:
        require_processes()
        status = evaluate_mission_logs(recent_logs(), expected_targets)
        if status.failure:
            raise RuntimeError(f"ciclo da missão falhou: {status.failure}")
        progress = (status.undocked, status.completed_targets, status.docked)
        if progress != last_progress:
            if status.undocked:
                print("[OK] saída da doca confirmada")
            if status.completed_targets:
                print("[OK] metas concluídas: " + ", ".join(status.completed_targets))
            if status.docked:
                print("[OK] retorno à doca confirmado")
            last_progress = progress
        if status.docked and list(status.completed_targets) == expected_targets:
            return
        time.sleep(2)
    missing = ", ".join(
        target for target in expected_targets if target not in (last_progress or (False, (), False))[1]
    )
    detail = f"; metas pendentes: {missing}" if missing else "; dock não confirmado"
    raise TimeoutError("o ciclo completo não terminou" + detail)


def read_odom() -> tuple[float, float] | None:
    command = (
        "source /opt/ros/humble/setup.bash && "
        "source /opt/maestro_ws/install/setup.bash && "
        "timeout 8 ros2 topic echo --once /turtlebot1/odom"
    )
    try:
        result = container_shell(command, timeout=12)
    except subprocess.TimeoutExpired:
        # A máquina pode estar ocupada renderizando Gazebo/RViz. Uma leitura
        # perdida não prova que o robô parou; wait_for_motion tentará de novo.
        return None
    if result.returncode:
        return None
    match_x = re.search(r"position:\s*\n\s*x:\s*([-+0-9.eE]+)", result.stdout)
    match_y = re.search(r"position:\s*\n\s*x:\s*[-+0-9.eE]+\s*\n\s*y:\s*([-+0-9.eE]+)", result.stdout)
    if not match_x or not match_y:
        return None
    return float(match_x.group(1)), float(match_y.group(1))


def wait_for_motion(
    initial_position: tuple[float, float], timeout_seconds: float
) -> tuple[float, float]:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        require_processes()
        position = read_odom()
        if position is not None and math.dist(position, initial_position) > 0.01:
            print(f"[OK] odometria alterada: x={position[0]:.3f}, y={position[1]:.3f}")
            return position
        print("Aguardando alteração da odometria...")
        time.sleep(2)
    raise TimeoutError("o robô não apresentou movimento na odometria")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verifica Gazebo, Nav2, meta e odometria.")
    parser.add_argument("--nav-timeout", type=float, default=150)
    parser.add_argument("--goal-timeout", type=float, default=120)
    parser.add_argument("--motion-timeout", type=float, default=60)
    parser.add_argument("--cycle-timeout", type=float, default=0)
    parser.add_argument(
        "--expected-target",
        action="append",
        dest="expected_targets",
        help="meta que deve terminar antes do dock; repita para validar uma rota",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        require_processes()
        require_no_fatal_render_error()
        print("[OK] Gazebo e bridge ativos")
        wait_for_nav2(args.nav_timeout)
        wait_for_goal(args.goal_timeout)
        initial_position = read_odom()
        if initial_position is None:
            raise RuntimeError("não foi possível obter a odometria inicial")
        print(
            f"[OK] odometria inicial: x={initial_position[0]:.3f}, "
            f"y={initial_position[1]:.3f}"
        )
        wait_for_motion(initial_position, args.motion_timeout)
        if args.cycle_timeout > 0:
            wait_for_mission_cycle(
                args.expected_targets or ["plot-03"],
                args.cycle_timeout,
            )
    except (RuntimeError, TimeoutError, subprocess.TimeoutExpired) as error:
        raise SystemExit(f"Erro: simulação não verificada: {error}") from None
    print("SIMULAÇÃO VERIFICADA: protocolo, Nav2 e movimento confirmados")


if __name__ == "__main__":
    main()
