#!/usr/bin/env bash
# Nightly backup: pg_dump of the factory DB + (optional) sync of object storage.
# Designed to be cron-driven on the host:
#   0 3 * * *  /opt/factory/deploy/scripts/backup.sh >> /var/log/factory-backup.log 2>&1
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
mkdir -p "$BACKUP_DIR"
TS="$(date -u +%Y%m%dT%H%M%SZ)"

source .env

DUMP="$BACKUP_DIR/factory-$TS.sql.gz"
echo "→ pg_dump → $DUMP"
docker compose exec -T postgres \
  pg_dump -U "${POSTGRES_USER:-factory}" -d "${POSTGRES_DB:-factory}" --no-owner --no-privileges \
  | gzip -9 > "$DUMP"

# Keep last 14 daily dumps locally
ls -1t "$BACKUP_DIR"/factory-*.sql.gz | tail -n +15 | xargs -r rm -f --

# Optional: push to S3-compatible storage (uses settings already in .env)
if [[ -n "${BACKUP_S3_BUCKET:-}" ]]; then
  echo "→ Uploading dump to s3://$BACKUP_S3_BUCKET/"
  docker run --rm -v "$(pwd)/$BACKUP_DIR:/b" \
    -e AWS_ACCESS_KEY_ID="${S3_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${S3_SECRET_ACCESS_KEY}" \
    amazon/aws-cli:latest s3 cp "/b/$(basename "$DUMP")" "s3://$BACKUP_S3_BUCKET/$(basename "$DUMP")" \
    ${S3_ENDPOINT_URL:+--endpoint-url "$S3_ENDPOINT_URL"}
fi

echo "✓ backup complete: $DUMP"
