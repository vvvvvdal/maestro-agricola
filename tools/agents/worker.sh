#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/common.sh"

if [ "$#" -lt 2 ]; then
  printf 'Usage: %s <research|test|implementation> <question>\n' "$0" >&2
  exit 2
fi

role="$1"
shift

case "$role" in
  research|test|implementation) ;;
  *)
    printf 'Unknown worker role: %s\n' "$role" >&2
    exit 2
    ;;
esac

require_test_jev_branch
require_command gemini

exec gemini --approval-mode plan --sandbox --output-format text -p \
  "You are the $role worker for Maestro Agricola on test/jev. $* Read only the minimum relevant files. Do not edit files, create worktrees, run mutating commands, access credentials, call external services, or make safety/product decisions. Return concise evidence with file paths, risks, and recommended focused tests."
