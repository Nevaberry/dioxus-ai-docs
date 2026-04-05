---
name: podman-knowledge-patch
description: Podman changes since training cutoff (latest: 5.8.0) — Quadlet CLI management, OCI artifacts, multi-file install, BoltDB→SQLite migration, TLS remote. Load before working with Podman.
version: "5.8.0"
license: MIT
metadata:
  author: Nevaberry
---

# Podman Knowledge Patch

Claude Opus 4.6 knows Podman through 4.x / early 5.x. This skill provides features from Podman 5.6 (2024-08-15) through 5.8 (2025-02-12).

## Index

| Topic | Reference | Key features |
|---|---|---|
| Quadlet | [references/quadlet.md](references/quadlet.md) | CLI management, multi-file install, `.artifact` type, new keys, REST API |
| CLI enhancements | [references/cli-enhancements.md](references/cli-enhancements.md) | `--creds`/`--cert-dir`, `--return-on-first`, `--no-session`, `--ulimit` update, `kube play` multi-file |
| OCI artifacts | [references/artifacts.md](references/artifacts.md) | Stable `podman artifact` commands, REST API, `podman inspect` artifacts |
| Infrastructure | [references/infrastructure.md](references/infrastructure.md) | TLS/mTLS remote, BoltDB→SQLite migration, `--swap`, Rosetta disabled, compat API changes |

---

## Quick Reference

### Quadlet management commands (5.6+)

```bash
podman quadlet install myapp.container # install for current user
podman quadlet list                    # list installed Quadlets
podman quadlet print myapp.container   # print file contents
podman quadlet rm myapp.container      # remove a Quadlet
```

Not available with remote client.

### Multi-file Quadlet install (5.8+)

Single file with multiple units separated by `---`:
```ini
# FileName=app.container
[Container]
Image=myapp:latest

---
# FileName=db.container
[Container]
Image=postgres:16
```
```bash
podman quadlet install combined.quadlet
```

---

### New Quadlet keys by version

| Version | File type | Key | Purpose |
|---|---|---|---|
| 5.7 | `.container` | `HttpProxy` | Control HTTP proxy forwarding into container |
| 5.7 | `.pod` | `StopTimeout` | Configure pod stop timeout |
| 5.7 | `.build` | `BuildArg` | Specify build arguments |
| 5.7 | `.build` | `IgnoreFile` | Specify ignore file |
| 5.7 | `.kube` | *(multi-YAML)* | Multiple YAML files in single `.kube` file |
| 5.8 | `.container` | `AppArmor` | Set container's AppArmor profile |

---

### OCI artifacts (stable since 5.6)

```bash
podman artifact pull oci-registry.example/myartifact:v1
podman artifact ls
podman artifact inspect myartifact
podman artifact push myartifact docker://registry/repo:tag
podman artifact rm myartifact
podman artifact add myartifact file1.tar file2.tar
podman artifact extract myartifact
```

Available via remote client. `podman inspect` can also inspect artifacts (5.7+).

### Artifact REST API (5.6+)

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/libpod/artifacts/json` | List artifacts |
| `GET` | `/libpod/artifacts/{name}/json` | Inspect artifact |
| `POST` | `/libpod/artifacts/pull` | Pull artifact |
| `DELETE` | `/libpod/artifacts/{name}` | Remove artifact |
| `POST` | `/libpod/artifacts/add` | Add artifact from tar |
| `POST` | `/libpod/artifacts/{name}/push` | Push to registry |
| `GET` | `/libpod/artifacts/{name}/extract` | Get artifact contents |

---

### Quadlet REST API (5.8+)

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/libpod/quadlets` | Install Quadlets |
| `GET` | `/libpod/quadlets/{name}/file` | Print Quadlet file contents |
| `GET` | `/libpod/quadlets/{name}/exists` | Check if Quadlet exists |
| `DELETE` | `/libpod/quadlets` | Remove multiple Quadlets |
| `DELETE` | `/libpod/quadlets/{name}` | Remove a single Quadlet |

---

### Inline registry auth (5.7+)

```bash
podman run --creds user:pass --cert-dir /path/to/certs docker.io/myimage
```

### Multi-file kube play (5.7+)

```bash
podman kube play app.yaml db.yaml
podman kube down app.yaml db.yaml
podman kube play --no-pod-prefix app.yaml # don't prefix container names with pod name
```

### Wait for any container (5.7+)

```bash
podman wait --return-on-first --condition=exited ctr1 ctr2
```

### Fast exec without session tracking (5.8+)

```bash
podman exec --no-session mycontainer ls /app
```

### Update ulimits on running container (5.8+)

```bash
podman update --ulimit nofile=65536:65536 mycontainer
```

### Volume ownership (5.6+)

```bash
podman volume create --uid 1000 --gid 1000 myvolume
```

### VM swap (5.6+)

```bash
podman machine init --swap 2048   # size in megabytes
```

---

### TLS/mTLS for remote connections (5.7+)

Remote client and `podman system service` support TLS and mTLS encryption, including client certificate authentication. `podman system connection add` can create TLS-encrypted TCP connections.

---

### BoltDB → SQLite migration

- **5.6**: Deprecation warning added for BoltDB users
- **5.7**: Warnings visible by default
- **5.8**: Auto-migrates BoltDB to SQLite on reboot. Manual migration:
```bash
podman system migrate --migrate-db
```
BoltDB removal planned for Podman 6.0.

---

### Breaking changes

| Version | Change |
|---|---|
| 5.6 | Rosetta disabled by default in `podman machine` VMs (kernel compatibility issues) |
| 5.7 | Compat Image Inspect API: `ContainerConfig` field removed (use `Config` instead, matches Docker v1.45) |

---

## Reference Files

| File | Contents |
|---|---|
| [quadlet.md](references/quadlet.md) | CLI management commands, multi-file install, `.artifact` file type, new keys (HttpProxy, StopTimeout, BuildArg, IgnoreFile, AppArmor), REST API endpoints |
| [cli-enhancements.md](references/cli-enhancements.md) | `--creds`/`--cert-dir`, `kube play` multi-file + `--no-pod-prefix`, `--return-on-first`, `--no-session`, `--ulimit` update, `--uid`/`--gid` volumes, `--swap` |
| [artifacts.md](references/artifacts.md) | Stable artifact commands, REST API endpoints, `podman inspect` artifact support |
| [infrastructure.md](references/infrastructure.md) | TLS/mTLS remote connections, BoltDB deprecation and auto-migration, Rosetta disabled, compat API breaking change |
