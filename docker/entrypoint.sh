#!/usr/bin/env bash
set -euo pipefail

APP_MODULE="${APP_MODULE:-app.main:app}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
ALEMBIC_RETRIES="${ALEMBIC_RETRIES:-15}"
ALEMBIC_SLEEP_SECONDS="${ALEMBIC_SLEEP_SECONDS:-2}"

for attempt in $(seq 1 "$ALEMBIC_RETRIES"); do
  if alembic upgrade head; then
    break
  fi

  if [[ "$attempt" -eq "$ALEMBIC_RETRIES" ]]; then
    echo "Alembic migrations failed after ${ALEMBIC_RETRIES} attempts" >&2
    exit 1
  fi

  echo "Alembic failed, retrying in ${ALEMBIC_SLEEP_SECONDS}s (${attempt}/${ALEMBIC_RETRIES})" >&2
  sleep "$ALEMBIC_SLEEP_SECONDS"
done

exec uvicorn "$APP_MODULE" --host "$HOST" --port "$PORT" --proxy-headers --forwarded-allow-ips="*"

