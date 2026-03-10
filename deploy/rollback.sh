#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env.prod}"
STATE_FILE="${STATE_FILE:-$APP_DIR/deploy/state/last_api_image.txt}"

ROLLBACK_IMAGE="${1:-}"
if [[ -z "$ROLLBACK_IMAGE" ]]; then
  if [[ ! -f "$STATE_FILE" ]]; then
    echo "No rollback image provided and no state file found" >&2
    exit 1
  fi
  ROLLBACK_IMAGE="$(cat "$STATE_FILE")"
fi

export API_IMAGE="$ROLLBACK_IMAGE"

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d api
"$APP_DIR/deploy/wait_for_health.sh"

echo "Rollback completed with image $API_IMAGE"
