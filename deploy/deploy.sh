#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env.prod}"
STATE_DIR="${STATE_DIR:-$APP_DIR/deploy/state}"
API_SERVICE="${API_SERVICE:-api}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if [[ -z "${API_IMAGE:-}" ]]; then
  echo "API_IMAGE must be defined" >&2
  exit 1
fi

mkdir -p "$STATE_DIR"

PREVIOUS_CONTAINER_ID="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q "$API_SERVICE" || true)"
if [[ -n "$PREVIOUS_CONTAINER_ID" ]]; then
  docker inspect --format '{{.Config.Image}}' "$PREVIOUS_CONTAINER_ID" > "$STATE_DIR/last_api_image.txt"
fi

export API_IMAGE

docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d mysql minio
SERVICE_NAME=mysql "$APP_DIR/deploy/wait_for_health.sh"
"$APP_DIR/deploy/backup_mysql.sh"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" pull "$API_SERVICE"
docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d "$API_SERVICE"
"$APP_DIR/deploy/wait_for_health.sh"

echo "Deployment completed with image $API_IMAGE"
