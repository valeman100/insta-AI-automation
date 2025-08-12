#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}/.."

if [ -f "${REPO_ROOT}/.venv/bin/activate" ]; then
  source "${REPO_ROOT}/.venv/bin/activate"
  python "${REPO_ROOT}/main/main_ai.py"
  deactivate || true
else
  python3 "${REPO_ROOT}/main/main_ai.py"
fi