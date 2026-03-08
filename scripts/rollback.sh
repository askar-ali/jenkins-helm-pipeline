#!/usr/bin/env bash
# Usage: rollback.sh <env> [revision]   (default: previous revision)
set -euo pipefail

ENVIRONMENT="${1:?env (staging|prod)}"
REVISION="${2:-}"
RELEASE="sample-${ENVIRONMENT}"
NS="sample-${ENVIRONMENT}"

echo "History before rollback:"
helm history "$RELEASE" --namespace "$NS" --max 5

# shellcheck disable=SC2086
helm rollback "$RELEASE" $REVISION --namespace "$NS" --wait --timeout 5m
helm history "$RELEASE" --namespace "$NS" --max 3
