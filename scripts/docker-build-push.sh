#!/usr/bin/env bash
# Build Hugo locally, package into nginx image, push to Aliyun ACR.
#
# Usage:
#   ./scripts/docker-build-push.sh              # 1.0.0 + latest
#   ./scripts/docker-build-push.sh 1.0.1
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

REGISTRY="${REGISTRY:-registry.cn-beijing.aliyuncs.com}"
NAMESPACE="${NAMESPACE:-czbyte}"
IMAGE_NAME="${IMAGE_NAME:-mypage-blog}"
VERSION="${1:-${VERSION:-1.1.0}}"
FULL="${REGISTRY}/${NAMESPACE}/${IMAGE_NAME}"

if ! command -v hugo >/dev/null 2>&1; then
  echo "error: hugo not found in PATH" >&2
  exit 1
fi
if [[ ! -d themes/solitude ]]; then
  echo "error: themes/solitude missing — run: git submodule update --init --recursive" >&2
  exit 1
fi

NOTES_DIR="${NOTES_DIR:-$ROOT/../jiangbyte/Notes}"
PROJECTS_DIR="${PROJECTS_DIR:-$ROOT/../jiangbyte/Projects}"
if [[ -d "$NOTES_DIR" ]]; then
  python3 scripts/sync_notes.py "$NOTES_DIR"
fi
if [[ -d "$PROJECTS_DIR" ]]; then
  python3 scripts/sync_projects.py "$PROJECTS_DIR"
fi

echo "hugo --minify"
hugo --minify

echo "building ${FULL}:${VERSION}"
# ACR rejects BuildKit provenance/SBOM attestations (empty OCI manifest)
docker build \
  --provenance=false \
  --sbom=false \
  -t "${FULL}:${VERSION}" \
  -t "${FULL}:latest" \
  .

echo "pushing ${FULL}:${VERSION} and :latest"
docker push "${FULL}:${VERSION}"
docker push "${FULL}:latest"

echo "done"
echo "  docker pull ${FULL}:${VERSION}"
echo
echo "HTTP + HTTPS (jiangbyte.cn A/AAAA → server; 80/443 open):"
echo "  docker rm -f mypage-blog"
echo "  docker run -d --name mypage-blog --restart unless-stopped \\"
echo "    -p 80:80 -p 443:443 \\"
echo "    -e SITE_DOMAIN=jiangbyte.cn \\"
echo "    -v mypage-blog-caddy:/data \\"
echo "    ${FULL}:${VERSION}"
