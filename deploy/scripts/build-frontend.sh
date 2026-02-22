#!/usr/bin/env bash
set -euo pipefail

# Build frontend and copy to static/ directory
# Run this locally before deploying

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
STATIC_DIR="$PROJECT_ROOT/static"

echo "Building frontend..."
cd "$FRONTEND_DIR"
bun install --frozen-lockfile
bun run build

echo "Copying build output to static/..."
rm -rf "$STATIC_DIR"
cp -r "$FRONTEND_DIR/dist" "$STATIC_DIR"

echo "Frontend build complete: $STATIC_DIR"
