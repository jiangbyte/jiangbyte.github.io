# syntax=docker/dockerfile:1
# Expects prebuilt static site in ./public (run hugo --minify first).
# HTTP :80 always; set SITE_DOMAIN (+ optional ACME_EMAIL) for auto HTTPS :443.
FROM caddy:2.9-alpine

COPY docker/Caddyfile.http /etc/caddy/Caddyfile.http
COPY docker/Caddyfile.https /etc/caddy/Caddyfile.https
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY public/ /srv/

EXPOSE 80 443
VOLUME ["/data", "/config"]

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1/ >/dev/null || exit 1

ENTRYPOINT ["/entrypoint.sh"]
