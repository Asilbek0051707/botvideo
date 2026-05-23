#!/usr/bin/env bash
# Restore a pg_dump backup into the running Postgres container.
#   bash deploy/scripts/restore.sh ./backups/factory-2026XXXX.sql.gz
set -euo pipefail

DUMP="${1:?path to .sql.gz backup required}"
source .env

echo "⚠️  This will OVERWRITE the database '${POSTGRES_DB:-factory}'. Ctrl-C in 5s to abort."
sleep 5

gunzip -c "$DUMP" | docker compose exec -T postgres \
  psql -U "${POSTGRES_USER:-factory}" -d "${POSTGRES_DB:-factory}" -v ON_ERROR_STOP=1

echo "✓ restore complete"
