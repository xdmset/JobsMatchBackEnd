#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="${COMPOSE_FILE:-$APP_DIR/docker-compose.prod.yml}"
ENV_FILE="${ENV_FILE:-$APP_DIR/.env.prod}"
SERVICE_NAME="${SERVICE_NAME:-api}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-20}"
SLEEP_SECONDS="${SLEEP_SECONDS:-5}"

for attempt in $(seq 1 "$MAX_ATTEMPTS"); do
  CONTAINER_ID="$(docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps -q "$SERVICE_NAME")"
  if [[ -n "$CONTAINER_ID" ]]; then
    STATUS="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$CONTAINER_ID")"
    if [[ "$STATUS" == "healthy" || "$STATUS" == "running" ]]; then
      echo "Service $SERVICE_NAME is healthy"
      exit 0
    fi
  fi

  echo "Waiting for $SERVICE_NAME health (${attempt}/${MAX_ATTEMPTS})"
  sleep "$SLEEP_SECONDS"
done

echo "Service $SERVICE_NAME did not become healthy in time" >&2
exit 1

