#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "$0")/common.sh"

if [ "$#" -lt 2 ]; then
  printf 'Usage: %s <research|test|implementation> [--file <tracked-relative-path>]... <question>\n' "$0" >&2
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
require_command agy

context_files=(AGENTS.md GEMINI.md)

while [ "$#" -gt 1 ] && [ "$1" = "--file" ]; do
  context_files+=("$2")
  shift 2
done

question="$*"

for file in "${context_files[@]}"; do
  case "$file" in
    /*|../*|*/../*|.|..|*.env|*.env.*|*credentials*|*secret*|*token*|*key*)
      printf 'Unsafe context path: %s\n' "$file" >&2
      exit 2
      ;;
  esac

  if [ ! -f "$PROJECT_ROOT/$file" ]; then
    printf 'Context file not found: %s\n' "$file" >&2
    exit 2
  fi

  if ! git ls-files --error-unmatch -- "$file" >/dev/null 2>&1; then
    printf 'Context file must be tracked: %s\n' "$file" >&2
    exit 2
  fi
done

context=""
for file in "${context_files[@]}"; do
  context+=$'\n\n--- BEGIN '"$file"$' ---\n'
  context+="$(sed -n '1,500p' "$PROJECT_ROOT/$file")"
  context+=$'\n--- END '"$file"$' ---'
done

exec agy --sandbox --print-timeout 2m --output-format text -p \
  "You are the $role worker for Maestro Agricola on test/jev. Analyze only the supplied context bundle; do not invoke any tool or shell command. Do not edit files, create worktrees, access credentials, call external services, or make safety/product decisions. Answer only what the task requests. Every factual claim must cite a supplied context file. AGENTS.md and GEMINI.md are policy context, not evidence for source locations, test locations, test commands, runtime behavior, or results unless the task explicitly asks about policy. Do not infer missing files, commands, or outcomes. If the task cannot be answered from the supplied non-policy files, reply INSUFFICIENT_CONTEXT and state the types of additional files needed. Name an exact --file path only when that path appears in the supplied context.\n\nTask:\n$question\n\nContext bundle:$context"
