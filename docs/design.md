# Design

- **Fail fast**: tests and chart lint run before any image is built.
- **Security gate**: Trivy blocks HIGH/CRITICAL images before they reach the registry.
- **Safe deploys**: `helm --atomic` rolls back on failure; smoke test verifies after.
- **Promotion**: same image tag goes staging -> prod; prod needs a manual approval.
- **Credentials** are Jenkins credentials (`registry-creds`, `kubeconfig-*`), never in the repo.
- **Not covered**: Jenkins agent provisioning, notifications, SBOM/signing.

Not executed on a live Jenkins here; tests and `helm lint` were run locally.

## Additions
- Parallel verify/scan stages reduce wall-clock time; SBOM is generated alongside the gate.
- `--ignore-unfixed` avoids failing builds on vulnerabilities nobody can patch yet.
- Zero-unavailable rolling updates plus a PDB keep the service up during deploys and node drains.
