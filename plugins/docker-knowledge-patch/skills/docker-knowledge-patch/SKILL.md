---
name: docker-knowledge-patch
description: "Docker changes since training cutoff (latest: 0.31.0) — Rego source policies, bake --var flag, semvercmp function, env lookup disable. Load before working with Docker."
version: "0.31.0"
license: MIT
metadata:
  author: Nevaberry
---

# Docker Knowledge Patch

Claude Opus 4.6 knows Docker Engine through 24.x and Compose through 2.x. This skill provides features from Buildx 0.31.0 (2026-01-22).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Buildx & Bake | [references/buildx-bake.md](references/buildx-bake.md) | Rego source policies, `--var` flag, `semvercmp`, env lookup disable |

---

## Quick Reference

### Source policy enforcement with Rego (Buildx 0.31.0)

Buildx enforces build policies written in Rego (Open Policy Agent). Policies control what sources/images are allowed during builds.

```bash
# Explicit policy file
docker buildx build --policy policy.rego .

# Auto-loads Dockerfile.rego or app.Dockerfile.rego alongside the Dockerfile
docker buildx build -f app.Dockerfile .

# Evaluate and test policies
docker buildx policy eval
docker buildx policy test
```

In Bake, use the `policy` key or rely on auto-loading:

```hcl
# docker-bake.hcl
target "app" {
  dockerfile = "Dockerfile"
  policy     = "policy.rego"
}
```

---

### Bake `--var` flag (Buildx 0.31.0)

Set HCL variables directly from the command line instead of using environment variables:

```bash
docker buildx bake --var FOO=bar --var VERSION=1.2.3
```

---

### Bake `semvercmp` function (Buildx 0.31.0)

Stdlib function for semantic version comparisons in Bake HCL files.

---

### Bake env lookup disable (Buildx 0.31.0)

Option to prevent Bake from reading host environment variables, useful for reproducible builds.

---

## Reference Files

| File | Contents |
|---|---|
| [buildx-bake.md](references/buildx-bake.md) | Rego source policy enforcement (auto-loading, explicit `--policy`, `policy eval`/`test`, Bake `policy` key), `--var` flag for HCL variables, `semvercmp` stdlib function, env lookup disable |
