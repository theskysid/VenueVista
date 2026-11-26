#!/usr/bin/env bash
# Run in the staging directory containing .env, compose.deploy.yaml and helpers.
set -euo pipefail
repository="${1:?Usage: deploy.sh owner/repository sha-COMMIT}"
tag="${2:?Usage: deploy.sh owner/repository sha-COMMIT}"
[[ "$repository" =~ ^[a-z0-9._-]+/[a-z0-9._-]+$ ]] || { echo 'Invalid image repository' >&2; exit 1; }
[[ "$tag" =~ ^sha-[0-9a-f]{40}$ ]] || { echo 'Expected a full commit SHA image tag' >&2; exit 1; }
test -f .env && test -f compose.deploy.yaml && test -f check_health.sh
mkdir -p releases
# One deployment at a time, including direct/manual executions on this server.
exec 9>.deploy.lock
flock -n 9 || { echo 'A deployment is already in progress' >&2; exit 1; }
release="releases/${tag}.env"
printf 'IMAGE_REPOSITORY=%s\nIMAGE_TAG=%s\n' "$repository" "$tag" > "$release"
compose=(docker compose --env-file .env --env-file "$release" -f compose.deploy.yaml)
"${compose[@]}" config --quiet
"${compose[@]}" pull backend frontend
if test -f current.env; then cp current.env previous.env; fi
restore_previous() {
  echo 'Deployment failed; attempting to restore the previous image pair.' >&2
  if test -f previous.env; then
    docker compose --env-file .env --env-file previous.env -f compose.deploy.yaml up -d --wait --wait-timeout 600 backend frontend || true
  else
    echo 'There is no previous successful release to restore.' >&2
  fi
}
trap restore_previous ERR
"${compose[@]}" up -d --wait --wait-timeout 900
# Read UI_PORT as data; never source the server secret file as shell code.
ui_port="$(sed -n 's/^UI_PORT=\([0-9][0-9]*\)$/\1/p' .env | tail -1)"
bash check_health.sh "http://localhost:${ui_port:-4200}"
cp "$release" current.env
trap - ERR
echo "Deployed VenueVista P_014 release $tag"
