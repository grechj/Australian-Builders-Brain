#!/usr/bin/env bash
# Give the skills a Python with python-docx, openpyxl and PyYAML.
# Builds a venv in the plugin's data folder (kept across plugin updates) the
# first time, and again only when requirements.txt changes. Never fails the
# session: if anything goes wrong, the skills fall back to python3 and pip.
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
DATA="${CLAUDE_PLUGIN_DATA:-}"
[ -n "$ROOT" ] && [ -n "$DATA" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

VENV="$DATA/venv"
STAMP="$VENV/.requirements_sha256"
# reportlab only builds the brain's own PDFs, so the skills don't need it.
REQS=$(grep -v -e '^\s*#' -e 'reportlab' "$ROOT/requirements.txt" | sed 's/#.*//' | grep -v '^\s*$')
SHA=$(printf '%s' "$REQS" | shasum -a 256 2>/dev/null | cut -d' ' -f1)

[ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$SHA" ] && exit 0
{
  python3 -m venv "$VENV" &&
  printf '%s\n' "$REQS" > "$DATA/requirements_runtime.txt" &&
  "$VENV/bin/python" -m pip install --quiet --disable-pip-version-check -r "$DATA/requirements_runtime.txt" &&
  printf '%s' "$SHA" > "$STAMP"
} >/dev/null 2>&1 || true
exit 0
