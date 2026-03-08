#!/usr/bin/env bash
# Usage: deploy.sh <env> <image-tag>
# Uses the per-environment values file, --atomic (auto rollback on failed rollout),
# then runs the chart's helm test.
set -euo pipefail
cd "$(dirname "$0")/.."

ENVIRONMENT="${1:?env (staging|prod)}"
TAG="${2:?image tag}"
REGISTRY="${REGISTRY:-registry.example.internal}"
VALUES="chart/values-${ENVIRONMENT}.yaml"
[[ -f "$VALUES" ]] || { echo "no values file: $VALUES" >&2; exit 1; }

RELEASE="sample-${ENVIRONMENT}"
NS="sample-${ENVIRONMENT}"

helm upgrade --install "$RELEASE" chart \
  --namespace "$NS" --create-namespace \
  -f "$VALUES" \
  --set image.repository="${REGISTRY}/sample" \
  --set image.tag="${TAG}" \
  --atomic --timeout 5m

helm test "$RELEASE" --namespace "$NS" --timeout 2m
