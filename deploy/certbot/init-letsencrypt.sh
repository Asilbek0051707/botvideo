#!/usr/bin/env bash
# One-time TLS bootstrap: issue Let's Encrypt cert via webroot through nginx.
# Run from the project root once nginx (prod profile) is up on port 80.
#
# Usage:   DOMAIN=your-domain.com EMAIL=you@your-domain.com bash deploy/certbot/init-letsencrypt.sh
set -euo pipefail

: "${DOMAIN:?DOMAIN is required}"
: "${EMAIL:?EMAIL is required}"
STAGING="${STAGING:-0}"

mkdir -p deploy/certbot/conf deploy/certbot/www

echo "→ Issuing certificate for $DOMAIN (staging=$STAGING)"

ARGS=( --webroot -w /var/www/certbot \
       -d "$DOMAIN" \
       --email "$EMAIL" --agree-tos --no-eff-email --non-interactive --rsa-key-size 4096 )
[[ "$STAGING" == "1" ]] && ARGS+=( --staging )

docker run --rm \
  -v "$(pwd)/deploy/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/deploy/certbot/www:/var/www/certbot" \
  certbot/certbot:latest certonly "${ARGS[@]}"

echo "→ Reloading nginx"
docker compose --profile prod exec nginx nginx -s reload

echo "✓ Done. Renew with:  bash deploy/certbot/renew.sh"
