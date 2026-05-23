#!/usr/bin/env bash
# Renew Let's Encrypt certs (idempotent; safe to cron daily).
set -euo pipefail

docker run --rm \
  -v "$(pwd)/deploy/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/deploy/certbot/www:/var/www/certbot" \
  certbot/certbot:latest renew --webroot -w /var/www/certbot --quiet

docker compose --profile prod exec nginx nginx -s reload
