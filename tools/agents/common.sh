#!/usr/bin/env bash

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$PROJECT_ROOT"

# Gemini is installed through nvm on this workstation. Source it only when a
# caller did not inherit the interactive shell PATH.
if ! command -v gemini >/dev/null 2>&1 && [ -s "${NVM_DIR:-$HOME/.nvm}/nvm.sh" ]; then
  # shellcheck disable=SC1090
  . "${NVM_DIR:-$HOME/.nvm}/nvm.sh"
fi

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'Missing required command: %s\n' "$1" >&2
    exit 1
  fi
}

require_test_jev_branch() {
  local branch
  branch="$(git branch --show-current)"
  if [ "$branch" != "test/jev" ]; then
    printf 'This workflow only runs on test/jev (current: %s).\n' "${branch:-detached}" >&2
    exit 1
  fi
}
