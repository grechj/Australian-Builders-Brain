#!/usr/bin/env bash
# Give the skills a Python with python-docx, openpyxl, PyYAML and pdfplumber.
# Builds a venv in the plugin's data folder (kept across plugin updates) the
# first time, and again only when hooks/requirements_runtime.txt changes. It
# installs only the exact versions listed there, from PyPI. Never fails the
# session: if anything goes wrong, the skills fall back to python3 and pip.
ROOT="${CLAUDE_PLUGIN_ROOT:-}"
DATA="${CLAUDE_PLUGIN_DATA:-}"
[ -n "$ROOT" ] && [ -n "$DATA" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

VENV="$DATA/venv"
STAMP="$VENV/.requirements_sha256"
REQS="$ROOT/hooks/requirements_runtime.txt"
SHA=$(shasum -a 256 "$REQS" 2>/dev/null | cut -d' ' -f1)

[ -f "$STAMP" ] && [ "$(cat "$STAMP")" = "$SHA" ] && exit 0
{
  python3 -m venv "$VENV" &&
  "$VENV/bin/python" -m pip install --quiet --disable-pip-version-check -r "$REQS" &&
  printf '%s' "$SHA" > "$STAMP"
} >/dev/null 2>&1 || true
exit 0
