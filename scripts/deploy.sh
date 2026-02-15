#!/usr/bin/env bash
# Usage: deploy.sh <env> <image-tag>
# --atomic rolls back automatically if the rollout is not healthy in time.
set -euo pipefail

ENVIRONMENT="${1:?env (staging|prod)}"
TAG="${2:?image tag}"
REGISTRY="${REGISTRY:-registry.example.internal}"

helm upgrade --install "sample-${ENVIRONMENT}" chart \
  --namespace "sample-${ENVIRONMENT}" --create-namespace \
  --set image.repository="${REGISTRY}/sample" \
  --set image.tag="${TAG}" \
  --atomic --timeout 5m
