#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /opt/maestro_ws/install/setup.bash

if [[ "${MAESTRO_HEADLESS:-1}" == "1" ]]; then
  export DISPLAY="${MAESTRO_VIRTUAL_DISPLAY:-:99}"
  display_number="${DISPLAY#:}"
  display_number="${display_number%%.*}"
  if [[ ! "${display_number}" =~ ^[0-9]+$ ]]; then
    echo "Invalid MAESTRO_VIRTUAL_DISPLAY: ${DISPLAY}" >&2
    exit 1
  fi

  display_lock="/tmp/.X${display_number}-lock"
  display_socket="/tmp/.X11-unix/X${display_number}"
  xvfb_log="/tmp/maestro-xvfb.log"
  mkdir -p /tmp/.X11-unix
  rm -f "${display_lock}" "${display_socket}"
  Xvfb "${DISPLAY}" -screen 0 1280x720x24 -ac +extension GLX +render -noreset \
    >"${xvfb_log}" 2>&1 &
  xvfb_pid=$!

  display_ready=0
  for _ in {1..100}; do
    if [[ -S "${display_socket}" ]]; then
      display_ready=1
      break
    fi
    if ! kill -0 "${xvfb_pid}" 2>/dev/null; then
      break
    fi
    sleep 0.1
  done

  if [[ "${display_ready}" != "1" ]]; then
    echo "Xvfb did not become ready on ${DISPLAY}" >&2
    cat "${xvfb_log}" >&2 || true
    exit 1
  fi
fi

simulation_share="$(ros2 pkg prefix maestro_simulation)/share/maestro_simulation"
export GZ_SIM_RESOURCE_PATH="${simulation_share}/models:${GZ_SIM_RESOURCE_PATH:-}"

exec "$@"
