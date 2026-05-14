#!/usr/bin/env bash
set -euo pipefail
BASEDIR="$(cd "$(dirname "$0")" && pwd)"
PY=python3

if ! command -v "$PY" >/dev/null 2>&1; then
  echo "python3 not found" >&2
  exit 2
fi

# Optional GITHUB_TOKEN is read by the script if needed in future
OUTDIR="${OUTDIR:-output}"
mkdir -p "$OUTDIR/scripts"
"$PY" "$BASEDIR/knowledge_silo_detector.py" --output "$OUTDIR" "$@"

