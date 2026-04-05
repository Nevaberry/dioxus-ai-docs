---
name: docker-knowledge-patch
description: "Docker changes since training cutoff (latest: Engine 29.3, Compose 5.1, Buildx 0.32) — Engine 29 breaking defaults, networking overhaul, image mounts, Compose service providers, Buildx Rego policies, CDI GPUs. Load before working with Docker."
version: "29.3"
license: MIT
metadata:
  author: Nevaberry
---

# Docker Knowledge Patch

Covers Docker Engine 28.0–29.3, Compose v2.30–v2.38, and Buildx 0.31.0+. Claude Opus 4.6 knows Docker through Engine 27.x and Compose v2.28. It is **unaware** of the Engine 28 networking overhaul, Engine 29 breaking defaults, and newer Compose/Buildx features below.

## Index

| Topic | Reference | Key features |
|---|---|---|
| Engine 29 | [references/engine-29.md](references/engine-29.md) | containerd default, DCT removed, cgroup v1 deprecated, nftables, fd limit 1024, image identity |
| Engine 28 | [references/engine-28.md](references/engine-28.md) | Networking overhaul, image mounts, CDI/AMD GPU, platform flags, `docker bake`, `--use-api-socket` |
| Compose features | [references/compose-features.md](references/compose-features.md) | Lifecycle hooks, watch enhancements, service providers, `models:` key, build with bake |
| Buildx & BuildKit | [references/buildx-and-buildkit.md](references/buildx-and-buildkit.md) | Rego source policies, `--var` flag, `semvercmp`, scoped config, BuildKit version map |

---

## Engine 29 Breaking Changes (Nov 2025)

The most impactful changes for existing workflows:

| Change | Impact |
|---|---|
| containerd image store is default (fresh installs) | Different image storage behavior, new `--tree` list view |
| Docker Content Trust removed from CLI | DCT only available as separate plugin |
| cgroup v1 deprecated | Warnings shown; migrate to cgroup v2 (removal after May 2029) |
| File descriptor limit → 1024 | Was 1048576; apps expecting high fd limit will break |
| Minimum API version → v1.44 | Clients older than Docker 25.0 rejected (relaxed to v1.40 in 29.3) |
| `DOCKER-ISOLATION-STAGE-1/2` chains removed | iptables rules using these chains will fail |
| Legacy links env vars removed | Use `DOCKER_KEEP_DEPRECATED_LEGACY_LINKS_ENV_VARS=1` to restore |
| `docker image ls` uses collapsed tree view | Default output format changed |
| Go module → `github.com/moby/moby/{client,api}` | `github.com/docker/docker` deprecated |

### nftables backend (experimental)

```json
{ "firewall-backend": "nftables" }
```

### Multi-platform load/save

```bash
docker image save --platform linux/amd64,linux/arm64 myimage > multi.tar
```

See [references/engine-29.md](references/engine-29.md) for all 29.x features.

---

## Engine 28 Networking Overhaul (Feb 2025)

Engine 28.0 significantly restructured iptables rules and networking security:

- **ipset kernel modules required** (`ip_set`, `ip_set_hash_net`) — softened in 28.0.1
- Remote/neighbor hosts can no longer connect directly to published container ports
- `docker-proxy` updated and incompatible with older `dockerd`
- Container interfaces use randomly-generated MAC addresses
- New gateway modes: `nat-unprotected`, `isolated`

### Image mounts (28.0)

```bash
docker run --mount type=image,source=alpine:latest,dst=/alpine myimage
docker run --mount type=image,source=tools:v1,dst=/tools,image-subpath=bin myimage
```

### CDI & GPU support (28.2+)

CDI enabled by default. AMD GPUs supported via `--gpus`:
```bash
docker run --gpus all myworkload  # AMD and NVIDIA via CDI (29.3+)
```

### `docker bake` alias (28.1)

```bash
docker bake  # top-level alias for docker buildx bake
```

### Platform-specific operations (28.0–28.2)

```bash
docker image inspect --platform linux/arm64 myimage
docker image rm --platform linux/arm64 myimage
docker ps --format '{{.Names}} {{.Platform}}'
```

### Relative bind mount paths (28.2)

```bash
docker run -v ../data:/data myimage
```

See [references/engine-28.md](references/engine-28.md) for networking details and all features.

---

## Compose Quick Reference (v2.30–v2.38)

### Lifecycle hooks (v2.30)

```yaml
services:
  web:
    post_start:
      - command: /app/warmup.sh
    pre_stop:
      - command: /app/drain.sh
```

### Watch: sync+exec (v2.32) and include filter (v2.34)

```yaml
develop:
  watch:
    - action: sync+exec
      path: ./src
      target: /app/src
      exec:
        command: npm run build
      include:
        - "**/*.ts"
```

### Build with Bake (v2.32)

```bash
COMPOSE_BAKE=1 docker compose build
```

### Refresh pull policy (v2.34)

```yaml
pull_policy: refresh  # always re-pull even if image exists locally
```

### Service provider plugins (v2.36)

```yaml
services:
  myservice:
    provider:
      type: my-custom-provider
      options:
        key: value
```

### `models:` top-level key (v2.38)

```yaml
models:
  my-model:
    model: ai/my-model:latest

services:
  app:
    depends_on:
      - my-model
```

### Other new commands

```bash
docker compose publish myregistry/myapp:v1 # publish OCI artifact (v2.34)
docker compose volumes                     # list project volumes (v2.38)
docker compose build --check               # validate without building (v2.36)
docker compose export web >fs.tar          # export filesystem (v2.30)
```

See [references/compose-features.md](references/compose-features.md) for all features.

---

## Buildx 0.31.0+ (Jan 2026)

### Rego source policies (experimental)

Buildx auto-loads `Dockerfile.rego` alongside `Dockerfile`:

```bash
docker buildx build --policy security.rego .
docker buildx policy eval my-policy.rego
docker buildx policy test my-policy.rego
```

### Bake `--var` flag

```bash
docker buildx bake --var VERSION=1.2.3 --var ENV=production
```

### `semvercmp` helper in Bake HCL

```hcl
target "app" {
  args = {
    USE_NEW_API = semvercmp(VERSION, "2.0.0") >= 0 ? "true" : "false"
  }
}
```

See [references/buildx-and-buildkit.md](references/buildx-and-buildkit.md) for all Buildx features.

---

## Engine 29.3 Notable Additions

| Feature | Usage |
|---|---|
| `bind-create-src` | `--mount type=bind,src=/new/path,dst=/data,bind-create-src` |
| Image identity | `docker image inspect` → `Identity` field (build ref, provenance) |
| NRI support | Experimental Node Resource Interface, shown in `docker info` |
| CDI GPU injection | `--gpus` uses CDI for AMD + NVIDIA |

---

## Reference Files

| File | Contents |
|---|---|
| [engine-29.md](references/engine-29.md) | Breaking defaults, nftables, multi-platform save/load, health API field, identity, NRI, bind-create-src, CDI GPUs |
| [engine-28.md](references/engine-28.md) | Networking overhaul (ipset, iptables, MAC, gateway modes), image mounts, CDI, platform flags, bake alias, relative paths, auth config |
| [compose-features.md](references/compose-features.md) | Lifecycle hooks, watch sync+exec/include, bake builds, refresh policy, service providers, models key, publish, volumes command |
| [buildx-and-buildkit.md](references/buildx-and-buildkit.md) | Rego source policies, --var flag, semvercmp, scoped config, BuildKit version map, behavior changes |
