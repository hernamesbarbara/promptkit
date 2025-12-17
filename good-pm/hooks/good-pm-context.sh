#!/bin/bash
# Good PM Context Injection Hook
# Conditionally injects PM context based on project detection
#
# This script is triggered by the UserPromptSubmit hook event.
# It only outputs context when the current directory is a Good PM project.
#
# Installation: Copied to .claude/hooks/ by /good-pm:setup
#
# Selective Loading:
# - Only injects if .good-pm/ directory exists in current directory
# - Prevents context pollution in non-PM projects
# - Preserves token budget for unrelated tasks

GOODPM_DIR=".good-pm"
CONTRACT="$GOODPM_DIR/context/PM_CONTRACT.md"
SESSION="$GOODPM_DIR/session/current.md"

# Early exit if not in a Good PM project
# This is the core of selective loading - no .good-pm/, no injection
if [ ! -d "$GOODPM_DIR" ]; then
  exit 0
fi

# Inject PM Contract if it exists
if [ -f "$CONTRACT" ]; then
  echo ""
  echo "[Good PM Context]"
  cat "$CONTRACT"
  echo ""
fi

# Inject session context if it exists and has meaningful content
# (not just the template with "(none)" placeholders)
if [ -f "$SESSION" ]; then
  # Check if file has content beyond template placeholders
  if grep -qvE '^\(none\)$|^#|^>|^-+$|^<!--.*-->$|^\*|^$' "$SESSION" 2>/dev/null; then
    echo ""
    echo "[Session Context]"
    cat "$SESSION"
    echo ""
  fi
fi

exit 0
