#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKUP_DIR="${BACKUP_DIR:-$APP_DIR/backups}"
MYSQL_CONTAINER_NAME="${MYSQL_CONTAINER_NAME:-jobmatch-mysql}"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/mysql_${TIMESTAMP}.sql"

mkdir -p "$BACKUP_DIR"

docker exec "$MYSQL_CONTAINER_NAME" sh -c \
  'exec mysqldump --single-transaction --quick -u"$MYSQL_USER" -p"$MYSQL_PASSWORD" "$MYSQL_DATABASE"' \
  > "$BACKUP_FILE"

echo "MySQL backup created at $BACKUP_FILE"

