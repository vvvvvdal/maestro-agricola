#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/common.sh"

if [ "$#" -eq 0 ]; then
  printf 'Usage: %s <task description>\n' "$0" >&2
  exit 2
fi

require_test_jev_branch
require_command codex

exec codex exec --profile maestro-planner --sandbox read-only --ephemeral \
  "Plan this Maestro Agricola task: $*. Read the repository rules and relevant files first. Return only: ambiguities, acceptance criteria, a small implementation plan, focused tests, and documentation updates. Do not edit files, run mutating commands, use credentials, or authorize product decisions."
