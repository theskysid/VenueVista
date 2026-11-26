#!/usr/bin/env bash
set -euo pipefail
base_url="${1:-http://localhost:4200}"
for attempt in {1..60}; do
  if curl --fail --silent --show-error --max-time 5 "$base_url/actuator/health" 2>/dev/null | python3 -c 'import sys,json;sys.exit(0 if json.load(sys.stdin).get("status")=="UP" else 1)' 2>/dev/null; then
    # A working health proxy must also serve the actual Angular page and API.
    curl --fail --silent --show-error --max-time 10 "$base_url/" | grep -q '<app-root'
    curl --fail --silent --show-error --max-time 10 "$base_url/api/events" | python3 -c 'import sys,json;assert isinstance(json.load(sys.stdin),list)'
    echo "VenueVista frontend, API and database are healthy."
    exit 0
  fi
  sleep 5
done
echo "VenueVista did not become healthy within the readiness window." >&2
exit 1
