# Buildx & BuildKit

Covers Buildx 0.31.0+ (January 2026) and BuildKit features bundled with Engine 28–29.

## Rego-Based Source Policies (Buildx 0.31.0, experimental)

Source policies written in [Rego](https://www.openpolicyagent.org/docs/policy-language) (Open Policy Agent language) enforce rules on build sources.

### Automatic policy loading

Buildx automatically loads policy files named after the Dockerfile:
- `Dockerfile.rego` for `Dockerfile`
- `app.Dockerfile.rego` for `app.Dockerfile`

### `--policy` flag

```bash
docker buildx build --policy my-policy.rego .
```

### `buildx policy` command

```bash
docker buildx policy eval my-policy.rego # evaluate a policy
docker buildx policy test my-policy.rego # test a policy
```

### Bake policy support

```hcl
target "app" {
  dockerfile = "Dockerfile"
  policy     = "security.rego"
}
```

---

## Bake `--var` Flag (Buildx 0.31.0)

Set Bake variable values from the command line without environment variables:

```bash
docker buildx bake --var VERSION=1.2.3 --var ENV=production
```

## `semvercmp` Bake Stdlib Helper (Buildx 0.31.0)

Semantic version comparison function available in Bake HCL:

```hcl
variable "VERSION" {
  default = "1.2.3"
}

target "app" {
  args = {
    USE_NEW_API = semvercmp(VERSION, "2.0.0") >= 0 ? "true" : "false"
  }
}
```

## Disable Bake Env Lookups (Buildx 0.31.0)

Prevent Bake from loading host environment variables and `.env` files (`--no-load-dotenv` style), for reproducible builds.

## Scoped Docker Config Loading (Buildx 0.31.0)

Finer credential control per repository/registry. Authentication falls back to Docker Hub credentials when pulling from Docker Hardened Images (dhi.io) and Docker Scout registries.

---

## BuildKit Features via Engine Packaging

Key BuildKit capabilities reached in Engine 28–29:

| Engine | BuildKit | Notable capability |
|---|---|---|
| 28.0 | v0.20 | `buildx prune` space filters (`reserved-space`, `max-used-space`, `min-free-space`, `keep-bytes`) |
| 28.2 | v0.22 | BuildKit GC enabled by default for containerd image store; Windows container image building |
| 29.0 | v0.25 | `device` entitlement in builder configuration |
| 29.2 | v0.27 | NRI support |
| 29.3 | v0.28 | `bind-create-src` mount option |

## Buildx Behavior Changes (0.31.0)

When creating images in Docker image store, images no longer unpack if the export was initialized with `--push` or `-o type=registry`. This avoids unnecessary local storage for push-only builds.
