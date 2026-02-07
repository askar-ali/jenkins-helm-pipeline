# jenkins-helm-pipeline

A Jenkins declarative pipeline with automated build, test, scan and deploy gates,
deploying to Kubernetes with Helm.

> Lab recreation of the CI/CD design I use in production (since 10/2025).
> Generic sample service and placeholder registry/cluster names.

## Pipeline

```
checkout -> lint+test -> docker build -> Trivy scan (gate) -> push
         -> helm deploy staging -> smoke test -> manual approval -> helm deploy prod
```

## Gates

| Gate | Fails the build when |
|------|----------------------|
| Unit tests | any test fails |
| Trivy | HIGH/CRITICAL vulnerabilities in the image |
| `helm upgrade --atomic` | rollout does not become ready (auto rollback) |
| Smoke test | `/healthz` not 200 after deploy |
| Approval | prod needs a human `input` on `main` only |

## Layout

```
app/        sample Python service + tests
Dockerfile  non-root, slim image
chart/      minimal Helm chart
Jenkinsfile pipeline
scripts/    deploy + smoke helpers (shell, usable outside Jenkins)
```

## Run the tests locally

```bash
python3 -m unittest discover -s app/tests
```
