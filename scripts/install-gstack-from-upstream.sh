#!/usr/bin/env bash
# Fetch upstream gstack + install to Windows and WSL Cursor skills.
# Run inside WSL: bash scripts/install-gstack-from-upstream.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export http_proxy= https_proxy= HTTP_PROXY= HTTPS_PROXY= ALL_PROXY=
rm -rf /tmp/gstack.tgz /tmp/gstack-extract /tmp/gstack-src
curl -fsSL --retry 3 -o /tmp/gstack.tgz \
  "https://codeload.github.com/garrytan/gstack/tar.gz/refs/heads/main"
mkdir -p /tmp/gstack-extract
tar -xzf /tmp/gstack.tgz -C /tmp/gstack-extract
SRC=$(ls -d /tmp/gstack-extract/gstack-* | head -1)
cp -a "$SRC" /tmp/gstack-src
bash "$ROOT/scripts/install-gstack-skills.sh"
echo "Inventory: $ROOT/docs/superpowers/qa/2026-07-27-gstack-skills-inventory.md"
