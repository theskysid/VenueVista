#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if ! command -v java >/dev/null || ! command -v mvn >/dev/null || ! command -v npm >/dev/null; then
  echo "Install Java 21, Maven 3.9+, and Node.js 20.19+ or 22.12+ first." >&2
  exit 1
fi
(cd backend && mvn -B package)
(cd frontend && npm ci && npm run build)
(cd backend && exec java -jar target/venuevista-1.0.0.jar) &
api_pid=$!
trap 'kill "$api_pid" 2>/dev/null || true' EXIT INT TERM
node scripts/preview.mjs
