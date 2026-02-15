#!/usr/bin/env bash
# Usage: smoke-test.sh <env>  (retries /healthz through a port-forward)
set -euo pipefail

ENVIRONMENT="${1:?env}"
NS="sample-${ENVIRONMENT}"
kubectl -n "$NS" port-forward "svc/sample-${ENVIRONMENT}" 18080:80 >/dev/null &
PF=$!
trap 'kill $PF 2>/dev/null || true' EXIT

for i in $(seq 1 10); do
  if curl -fsS http://localhost:18080/healthz >/dev/null; then
    echo "smoke test passed"; exit 0
  fi
  sleep 2
done
echo "smoke test FAILED" >&2
exit 1
