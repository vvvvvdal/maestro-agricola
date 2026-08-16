#!/usr/bin/env bash
set -eo pipefail

source /opt/ros/humble/setup.bash
source /opt/maestro_ws/install/setup.bash

if [[ "${MAESTRO_HEADLESS:-1}" == "1" ]]; then
  export DISPLAY="${MAESTRO_VIRTUAL_DISPLAY:-:99}"
  Xvfb "${DISPLAY}" -screen 0 1280x720x24 -ac +extension GLX +render -noreset &
fi

simulation_share="$(ros2 pkg prefix maestro_simulation)/share/maestro_simulation"
export GZ_SIM_RESOURCE_PATH="${simulation_share}/models:${GZ_SIM_RESOURCE_PATH:-}"

exec "$@"
