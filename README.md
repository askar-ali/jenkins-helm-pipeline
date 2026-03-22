# jenkins-helm-pipeline

A Jenkins declarative pipeline with automated build, test, scan and deploy gates,
deploying to Kubernetes with Helm.

> Lab recreation of the CI/CD design I use in production (since 10/2025).
> Generic sample service and placeholder registry/cluster names.

## Pipeline

```
checkout -> [unit tests | chart lint | shellcheck] -> docker build
         -> [Trivy gate | SBOM] -> push -> helm deploy staging (+ helm test, smoke)
         -> manual approval -> helm deploy prod (+ helm test, smoke)
```

## Gates

| Gate | Fails the build when |
|------|----------------------|
| Unit tests | any test fails |
| Trivy | HIGH/CRITICAL vulnerabilities in the image |
| `helm upgrade --atomic` | rollout does not become ready (auto rollback) |
| Smoke test | `/healthz` not 200 after deploy |
| Approval | prod needs a human `input` (release-managers) on `main` only |
| `helm test` | chart's `/healthz` test pod fails after deploy |

## Layout

```
app/        sample Python service + tests
Dockerfile  non-root, slim image
chart/      minimal Helm chart
Jenkinsfile pipeline; Jenkinsfile.rollback = parameterised rollback job
scripts/    deploy + smoke helpers (shell, usable outside Jenkins)
```

## Run the tests locally

```bash
python3 -m unittest discover -s app/tests
```

## Operations

- Roll back: run the `Jenkinsfile.rollback` job, or `scripts/rollback.sh <env> [revision]`.
- Every image carries OCI labels and `APP_VERSION`; `/metrics` exposes `app_info{version=...}`.
- A CycloneDX SBOM is archived with each build.

## Verified vs not

Verified locally: unit/integration tests (6), SIGTERM shutdown, `helm lint` and `helm template`
for staging and prod, `bash -n` on scripts. Not run here: the Jenkins pipelines themselves
(no Jenkins server), the Docker build, Trivy, or any real cluster.
