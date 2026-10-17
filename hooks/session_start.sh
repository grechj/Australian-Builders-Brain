#!/usr/bin/env bash
# At the start of each session: make sure the tools' Python is ready, then
# tell Claude where the user's jobs folder stands, so it can welcome a new
# user or open with a short briefing. Reads local files only; sends nothing.
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
[ -n "$ROOT" ] || exit 0
"$ROOT/hooks/setup_python.sh"
PY="${CLAUDE_PLUGIN_DATA:-}/venv/bin/python"
[ -x "$PY" ] || PY="python3"
FOLDER="${CLAUDE_PROJECT_DIR:-$PWD}"
"$PY" "$ROOT/tools/start.py" brief "$FOLDER" --hook 2>/dev/null || true
exit 0
