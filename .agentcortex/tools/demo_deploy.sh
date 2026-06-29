#!/usr/bin/env bash
# demo_deploy.sh — paved one-command demonstration of the adopter-visible deploy output.
#
# Usage: bash .agentcortex/tools/demo_deploy.sh
#
# Deploys into a fresh temp dir, prints the adopter-visible view:
#   1. Head of the deployed .agentcortex/context/current_state.md
#   2. Dry-run install inventory (tier + file)
# Exits non-zero on deploy failure.
#
# AC-13: CI-enforced anchored test is test_deploy_manifest_snapshot in
#        tests/ci/test_deploy_tiering.py (tests/ci/fixtures/deploy_manifest_golden.txt).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DEPLOY_SH="$REPO_ROOT/.agentcortex/bin/deploy.sh"

WORK_DIR="$(mktemp -d)"
TARGET="$WORK_DIR/downstream"
mkdir -p "$TARGET"

cleanup() { rm -rf "$WORK_DIR"; }
trap cleanup EXIT

echo "=== demo_deploy: deploying into $TARGET ==="
if ! bash "$DEPLOY_SH" "$TARGET" >/dev/null 2>&1; then
    echo "ERROR: deploy.sh exited non-zero" >&2
    bash "$DEPLOY_SH" "$TARGET" >&2 || true
    exit 1
fi
echo "Deploy: OK"
echo ""

echo "=== Adopter-visible: deployed current_state.md (head 8) ==="
head -8 "$TARGET/.agentcortex/context/current_state.md"
echo ""

echo "=== Adopter-visible: install inventory (tier + file, first 30) ==="
bash "$DEPLOY_SH" --dry-run "$TARGET" 2>/dev/null \
    | grep -E '^\s+\[(NEW|UPDATE)\]' \
    | awk '{print $3, $4}' \
    | sed 's/[()]//g' \
    | head -30
echo ""
echo "=== demo_deploy complete ==="
