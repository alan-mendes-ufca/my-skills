#!/usr/bin/env bash
# Resolve symlinks so all four Antigravity skills share the same controller.
set -euo pipefail
script_dir=$(cd -- "$(dirname -- "$(readlink -f -- "$0")")" && pwd -P)
exec python3 -B "$script_dir/run-isolated-review.py" "$@"
