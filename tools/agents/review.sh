#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/common.sh"

scope="${*:-the current uncommitted changes}"

require_test_jev_branch
require_command codex

exec codex exec --profile maestro-reviewer --sandbox read-only --ephemeral \
  "Review $scope in Maestro Agricola. Read AGENTS.md and relevant specs. Report only actionable findings, ordered by severity, with file and line references, then residual test gaps. Do not edit files, run mutating commands, use credentials, or approve a change."
