#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/common.sh"

require_test_jev_branch
require_command codex
require_command agy
require_command agent-reach

printf 'branch: %s\n' "$(git branch --show-current)"
printf 'codex: %s\n' "$(codex --version)"
printf 'antigravity: %s\n' "$(agy --version)"
printf 'agent-reach: %s\n' "$(agent-reach --version)"
git diff --check
printf 'preflight: OK\n'
