#!/usr/bin/env bash
set -euo pipefail

# Export local AGE database to JSON files for server import
# Run this locally before data-import.yml playbook

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
EXPORT_DIR="$BACKEND_DIR/data/age-export"

echo "Exporting local AGE database to JSON..."
cd "$BACKEND_DIR"
uv run quranref-cli db export-json "$EXPORT_DIR"

echo "Export complete: $EXPORT_DIR"
ls -lh "$EXPORT_DIR"
