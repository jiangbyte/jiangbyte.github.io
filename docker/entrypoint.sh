#!/bin/sh
set -eu

if [ -n "${SITE_DOMAIN:-}" ]; then
  echo "Caddy: HTTP (:80 for IP) + HTTPS for ${SITE_DOMAIN}"
  if [ -n "${ACME_EMAIL:-}" ]; then
    {
      printf '{\n\temail %s\n}\n\n' "$ACME_EMAIL"
      cat /etc/caddy/Caddyfile.https
    } >/etc/caddy/Caddyfile
  else
    cp /etc/caddy/Caddyfile.https /etc/caddy/Caddyfile
  fi
else
  echo "Caddy: HTTP only (:80). Set SITE_DOMAIN for HTTPS."
  cp /etc/caddy/Caddyfile.http /etc/caddy/Caddyfile
fi

exec caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
